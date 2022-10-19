class Inventory_Object:
    def __init__(self, href, row, domain):
        #self.name = name
        self.href = href
        self.row = row
        self.domain = domain
        self.manufacturer = None
        self.availability = None
        self.price = None
        self.name = None
        self.sku = None
        self.comp = None
        self.last_update = None
        self.run_failed = False
