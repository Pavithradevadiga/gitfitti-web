from flask import Flask, render_template, request
import git
import datetime
import os
import shutil

app = Flask(__name__)


def getDates(year=None):
    if year:
        jan1 = datetime.datetime(
            year=year, month=1, day=1, hour=10, minute=20, second=59)
    else:
        jan1 = datetime.datetime.now() - datetime.timedelta(weeks=53)
        jan1 -= datetime.timedelta(microseconds=jan1.microsecond)

    def onDay(date, day): return date + \
        datetime.timedelta(days=(day-date.weekday()) % 7)
    first_sunday = onDay(jan1, 6)
    dates = [list() for x in range(7)]
    for x in range(52 * 7):
        dates[x % 7].append(first_sunday + datetime.timedelta(x))
    return dates


@app.route('/', methods=['GET', 'POST'])
def main():
    if request.method == 'GET':
        return render_template('main.html')
    # a = [[int(request.form[f'{i} {j}']) for j in range(52)] for i in range(7)]
    # text_to_render = request.form['text']
    # font = Font('Fonts/subway-ticker.ttf', 8)
    # try:
    #     text = repr(font.render_text(text_to_render, 52, 7))
    #     text_by_weekday = text.split('\n')
    #     for i in range(7):
    #         for j in range(52):
    #             if text_by_weekday[i][j] == '#':
    #                 a[i][j] = (a[i][j] + 1)%3
    #     return render_template('main.html', a=a)
    # except:
    #     return "error"
    a = [[int(request.form[f'{i} {j}']) for j in range(52)] for i in range(7)]

    def getActiveDates(dates):
        ad = []
        for i in range(7):
            for j in range(52):
                for k in range(a[i][j]):
                    ad.append(dates[i][j])
        return ad
    try:
        year = int(request.form['year'])
        dates = getActiveDates(getDates(year))
    except:
        dates = getActiveDates(getDates())
    name = request.form['username']
    email = request.form['email']
    author = git.Actor(name, email)

    repurl = "https://" + name + ":" + \
        request.form['password'] + "@" + request.form['repo'][8:]
    repname = repurl.split('/')[-1].split('.')[0]
    if not os.path.isdir(repname):
        try:
            git.cmd.Git().clone(repurl)
        except:
            return render_template('result.html', msg='ERROR! Could not clone the repo. Ensure that the remote repo exists and that you have access to it.', form=request.form)
    rep = git.Repo.init(repname)
    nc = int(request.form['nc'])
    for date in dates:
        for n in range(nc):
            rep.index.commit("made with love by gitfitti", author=author,
                             committer=author, author_date=date.isoformat())
    try:
        rep.remotes.origin.set_url(repurl)
    except:
        rep.create_remote('origin', repurl)
    try:
        rep.remotes.origin.push()
        shutil.rmtree(repname)
    except:
        shutil.rmtree(repname)
        return render_template('result.html', msg='ERROR! Could not push to the repo. Ensure that the remote repo exists and that you have access to it.', form=request.form)
    return render_template('result.html', msg=f"SUCCESS! Created {nc*len(dates)} commits as {name} [{email}] in {repname}", form=request.form)

if __name__ == "__main__":
    app.run()
