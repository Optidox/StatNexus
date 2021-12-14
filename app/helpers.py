from app import app

def add_commas(num):
    try:
        with_commas = '{:,}'.format(num)
    except TypeError:
        with_commas = num
    finally:
        return with_commas
