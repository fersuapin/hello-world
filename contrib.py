#!/usr/bin/env python3
"""Render a repository's commit history as a GitHub-style contribution heatmap.

Reads `git log` directly, so it works offline and needs nothing outside the
standard library. It also breaks commits down by author email, which is the
detail GitHub's own graph hides: a commit only lands on your profile if its
author email belongs to your account and it sits on the default branch.

    python3 contrib.py                  # trailing 12 months, current branch
    python3 contrib.py --year 2026      # one calendar year
    python3 contrib.py --author fer     # substring match on name or email
    python3 contrib.py --all            # every branch, not just this one
"""

import argparse
import collections
import datetime as dt
import subprocess
import sys

DAY = dt.timedelta(days=1)
MONTHS = "Jan Feb Mar Apr May Jun Jul Aug Sep Oct Nov Dec".split()
WEEKDAY_LABELS = ["", "Mon", "", "Wed", "", "Fri", ""]
PALETTE = [238, 22, 28, 34, 46]
BLOCK = "■"


def git_log(repo, every_branch):
    """Return (date, email, name) for each commit, newest first."""
    cmd = ["git", "-C", repo, "log", "--pretty=format:%aI%x09%aE%x09%aN"]
    if every_branch:
        cmd.insert(3, "--all")
    proc = subprocess.run(cmd, capture_output=True, text=True)
    if proc.returncode != 0:
        sys.exit(proc.stderr.strip() or "git log failed")

    commits = []
    for line in proc.stdout.splitlines():
        stamp, _, rest = line.partition("\t")
        email, _, name = rest.partition("\t")
        commits.append((dt.date.fromisoformat(stamp[:10]), email, name))
    return commits


def window(year):
    """Inclusive (start, end) dates, snapped so the grid starts on a Sunday."""
    if year:
        start, end = dt.date(year, 1, 1), dt.date(year, 12, 31)
    else:
        end = dt.date.today()
        start = end - 364 * DAY
    # Python weeks start Monday; GitHub columns start Sunday.
    return start - ((start.weekday() + 1) % 7) * DAY, end


def build_weeks(start, end):
    weeks, current, cursor = [], [], start
    while cursor <= end:
        current.append(cursor)
        if len(current) == 7:
            weeks.append(current)
            current = []
        cursor += DAY
    if current:
        current.extend([None] * (7 - len(current)))
        weeks.append(current)
    return weeks


def thresholds(counts):
    """Quartile cutoffs over active days, mirroring how GitHub shades cells."""
    active = sorted(c for c in counts if c > 0)
    if not active:
        return [1, 2, 3, 4]
    return [max(1, active[min(len(active) - 1, int(len(active) * q))]) for q in (0.25, 0.5, 0.75, 0.95)]


def level(count, cuts):
    if count == 0:
        return 0
    return sum(count >= cut for cut in cuts[:3]) + 1


def paint(text, color, enabled):
    return f"\033[38;5;{color}m{text}\033[0m" if enabled else text


def month_header(weeks, enabled):
    """Place a month label above the first week that opens a new month."""
    cells, last_month = [" "] * len(weeks), None
    for i, week in enumerate(weeks):
        first = next((d for d in week if d), None)
        if first and first.month != last_month:
            label = MONTHS[first.month - 1]
            if i + len(label) <= len(weeks) and all(cells[i + n] == " " for n in range(len(label))):
                cells[i:i + len(label)] = list(label)
            last_month = first.month
    return "    " + paint("".join(cells), 245, enabled)


def streaks(by_date, start, end):
    """Longest run of consecutive active days, and the run ending most recently."""
    longest = run = 0
    today = min(end, dt.date.today())
    cursor = start
    while cursor <= end:
        run = run + 1 if by_date.get(cursor) else 0
        longest = max(longest, run)
        cursor += DAY

    current, cursor = 0, today
    while cursor >= start and by_date.get(cursor):
        current += 1
        cursor -= DAY
    return longest, current


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--repo", default=".", help="repository path (default: current directory)")
    parser.add_argument("--year", type=int, help="calendar year instead of trailing 12 months")
    parser.add_argument("--author", help="substring matched against author name or email")
    parser.add_argument("--all", action="store_true", dest="every_branch",
                        help="include every branch (GitHub counts only the default branch)")
    parser.add_argument("--no-color", action="store_true")
    args = parser.parse_args()

    color = not args.no_color and sys.stdout.isatty()
    commits = git_log(args.repo, args.every_branch)
    if args.author:
        needle = args.author.lower()
        commits = [c for c in commits if needle in c[1].lower() or needle in c[2].lower()]
    if not commits:
        sys.exit("No commits matched.")

    start, end = window(args.year)
    by_date = collections.Counter(d for d, _, _ in commits if start <= d <= end)
    weeks = build_weeks(start, end)
    cuts = thresholds(by_date.values())

    print()
    print(month_header(weeks, color))
    for row in range(7):
        line = [f"{WEEKDAY_LABELS[row]:>3} "]
        for week in weeks:
            day = week[row]
            if day is None or day > dt.date.today():
                line.append(" ")
            else:
                line.append(paint(BLOCK, PALETTE[level(by_date[day], cuts)], color))
        print("".join(line))

    print()
    print("    " + "  ".join([
        paint("less", 245, color),
        *[paint(BLOCK, c, color) for c in PALETTE],
        paint("more", 245, color),
    ]))

    total = sum(by_date.values())
    longest, current = streaks(by_date, start, end)
    span = f"{args.year}" if args.year else f"{start + 6 * DAY} → {end}"
    print()
    plural = "" if len(by_date) == 1 else "s"
    print(f"    {total} commits across {len(by_date)} active day{plural}  ({span})")
    print(f"    longest streak {longest}d    current streak {current}d")
    if by_date:
        peak, count = by_date.most_common(1)[0]
        print(f"    busiest day {peak} with {count}")

    # The part that decides whether GitHub gives you credit.
    authors = collections.Counter(email for d, email, _ in commits if start <= d <= end)
    if authors:
        print()
        print(paint("    credited to (author email must be on your GitHub account):", 245, color))
        width = max(len(e) for e in authors)
        for email, count in authors.most_common():
            print(f"      {email:<{width}}  {count}")
    print()


if __name__ == "__main__":
    main()
