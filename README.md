# hello-world
Learning GitHub's Repositories

Hey everyone!

I'm Fernando, an aspiring Data Scientist from Guatemala who's just dipping his toes into GitHub.

I have no idea what i'm getting into.

Cheers!
F

---

## contrib.py

A contribution heatmap for any git repository, drawn in your terminal. No
dependencies, no API token, no network — it reads `git log` and renders the
same green-square grid GitHub puts on your profile.

```bash
python3 contrib.py                  # trailing 12 months, current branch
python3 contrib.py --year 2021      # one calendar year
python3 contrib.py --author fer     # substring match on author name or email
python3 contrib.py --all            # every branch, not just this one
```

```
    Dec   Feb Mar Apr May  Jun Jul Aug  Sep Oct  Nov Dec
    ■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■
Mon ■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■
    ■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■
Wed ■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■
    ■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■
Fri ■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■
    ■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■

    less  ■  ■  ■  ■  ■  more

    3 commits across 1 active day  (2021)
    longest streak 1d    current streak 0d
    busiest day 2021-04-15 with 3
```

It also prints a breakdown by author email, which is the part GitHub's own
graph never shows you.

### Why that breakdown matters

A commit only lands on your GitHub profile if **all** of these hold:

1. The **author email** is on your GitHub account. A commit authored as
   `someone@example.com` is invisible on your graph even though you pushed it.
2. The commit is on the repo's **default branch** (or `gh-pages`). Work sitting
   on a feature branch counts for nothing until it's merged.
3. The repo is **not a fork**.

Opening a pull request or an issue is counted separately, and does show up the
same day you open it.

So if your squares look emptier than your week felt, run `contrib.py --all` and
read the email breakdown first — it's usually reason 1 or reason 2, not a bug.
