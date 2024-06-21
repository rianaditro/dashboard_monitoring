from extentions.template import Page


def main_page(database):
    page = Page('Perangkat', database)

    # frontend section
    page.container_perangkat()
