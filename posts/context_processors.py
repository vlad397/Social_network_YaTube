import datetime as dt


def year(request):
    y = dt.datetime.now().year
    return {"year": y}
