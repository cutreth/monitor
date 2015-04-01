from monitor.models import Beer

def getAllBeer():
    all_beer = Beer.objects.all()
    return all_beer
