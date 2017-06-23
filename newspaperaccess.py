# -*- coding: utf-8 -*-
import json, os

ARCHIVE = "/datastore/newspaperarchive"

def papertopath(newspaper, year = None, month = None, day = None, archive = ARCHIVE):
    if year == None:
        return os.path.join(archive, newspaper)
    elif day == None or month == None:
        return os.path.join(archive, newspaper, year)
    else:
        if len(month) != 2:
            month = "{0:02d}".format(int(month))
        if len(day) != 2:
            try:
                day = "{0:02d}".format(int(day))
            except ValueError as e:
                pass
        return os.path.join(archive, newspaper, year, month + "_" + day + ".json")

class NewspaperAccessError(Exception):
    pass

class NoSuchDocumentFound(NewspaperAccessError):
    pass

class NoSuchPage(NewspaperAccessError):
    pass

class NoSuchNewspaper(NewspaperAccessError):
    def __init__(self, newspaper):
        # print("Couldn't find '{0}' in the Newspaper mapping".format(newspaper))
        ...

NEWSPAPERMAPPING = {"aberdeenjournal": "ANJO",
                    "theaberdeenweeklyjournal": "ANJO",
                    "birminghamdailypost": "BDPO",
                    "bristolmercury": "BLMY",
                    "baner": "BNER",
                    "belfastnewsletter": "BNWL",
                    "belfastnews-letter": "BNWL",
                    "brightonpatriot": "BRPT",
                    "caledonianmercury": "CNMR",
                    "thecaledonianmercury": "CNMR",
                    "champion": "CHPN",
                    "charter": "CHTR",
                    "chartist": "CHTT",
                    "chartistcircular": "CTCR",
                    "cobbetsweeklypoliticalregister": "CWPR",
                    "cobbets": "CWPR",
                    "dailynews": "DNLN",
                    "derbymercury": "DYMR",
                    "thederbymercury": "DYMR",
                    "theera": "ERLN",
                    "examiner": "EXLN",
                    "graphic": "GCLN",
                    "freemansjournal": "FRJO",
                    "freeman'sjournalanddailycommercialadvertiser": "FRJO",
                    "freemansjournalanddailycommercialadvertiser": "FRJO",
                    "freeman'sjournalanddailyadvertiser": "FRJO",
                    "freemansjournalanddailyadvertiser": "FRJO",
                    "genedl": "GNDL",
                    "goleuad": "GLAD",
                    "glasgowherald": "GWHD",
                    "hampshire/portsmouthtelegraph": "HPTE",
                    "hampshiretelegraphandsussexchronicle": "HPTE",
                    "hampshiretelegraph&amp;portsmouthgazette": "HPTE",
                    "hampshiretelegraphportsmouthgazette": "HPTE",
                    "hampshiretelegraphandsussexchronicleetc": "HPTE",
                    "hampshiretelegraph": "HPTE",
                    "hullpacket": "HLPA",
                    "hullpacketandoriginalweeklycommercial,literaryandgeneraladvertiser": "HLPA",
                    "hullpacketandhumbermercury": "HLPA",
                    "hullpacketandeastridingtimes": "HLPA",
                    "illustratedpolicenews": "IPNW",
                    "ipswichjournal": "IPJO",
                    "jacksonsoxfordjournal": "JOJL",
                    "leedsmercury": "LEMR",
                    "theleedsmercury": "LEMR",
                    "liverpoolmercury": "LVMR",
                    "lloydsillustratednewspaper": "LINP",
                    "lloydsillustrated": "LINP",
                    "lloydsweeklynewspaper": "LINP",
                    "lloydsweeklylondonnewspaper": "LINP",
                    "londondispatch": "LNDH",
                    "manchestertimes": "MRTM",
                    "themanchestertimes": "MRTM",
                    #"manchesterexaminer": "MREX",
                    #"themanchesterexaminer": "MREX",
                    #"manchesterexaminerandtimes": "MREX",
                    "morningchronicle": "MCLN",
                    "newcastlecourant": "NECT",
                    "northernecho": "NREC",
                    "northernliberator": "NRLR",
                    "northernstar": "NRSR",
                    "northernstarandleedsgeneraladvertiser": "NRSR",
                    "northernstarandleedsadvertiser": "NRSR",
                    "northwaleschronicle": "NRWC",
                    "oddfellow": "ODFW",
                    "operative": "OPTE",
                    "pallmallgazette": "PMGZ",
                    "poormansguardian": "PMGU",
                    "prestonchronicle": "PNCH",
                    "prestonchronicleandlancashireadvertiser": "PNCH",
                    "reynoldsnewspaper": "RDNP",
                    "southernstar": "SNSR",
                    "trewmansexeterflyingpost": "TEFP",
                    "westernmail": "WMCF",
}

NEWSPAPERS = list(set(NEWSPAPERMAPPING.values()))


class NewspaperArchive(object):
    def __init__(self, archive = ARCHIVE, cachelimit = 5):
        self.archive = archive
        self.CACHELIMIT = cachelimit
        self._cache = {}
        self._cachelist = []
    
    def guess_newspaper(self, newspapertitle):
        shortened = newspapertitle.replace(" ", "").replace("&", "").replace("'", "").replace("-", "").lower()
        if shortened in NEWSPAPERMAPPING:
            return NEWSPAPERMAPPING[shortened]
        elif "the" + shortened in NEWSPAPERMAPPING:
            return NEWSPAPERMAPPING["the"+shortened]
        elif shortened.startswith("the") and shortened[3:] in NEWSPAPERMAPPING:
            return NEWSPAPERMAPPING[shortened[3:]]
        raise NoSuchNewspaper(newspapertitle)
    
    def isnewspaper(self, newspaper):
        if newspaper not in NEWSPAPERS:
            try:
                newspaper = self.guess_newspaper(newspaper)
            except NoSuchNewspaper as e:
                return False
        return os.path.isdir(papertopath(newspaper))
    
    def _cachename(self, newspaper, year, month, day):
        return newspaper + year + month + day
    
    def _addtocache(self, jsondoc, newspaper, year, month, day):
        if len(self._cachelist) > self.CACHELIMIT:
            # remove the oldest jsondoc from memory
            del self._cache[self._cachelist.pop(0)]
        
        self._cache[self._cachename(newspaper, year, month, day)] = jsondoc
        self._cachelist.append(self._cachename(newspaper, year, month, day))
    
    def exists(self, newspaper, year, month, day, page = None, **otherkwparams):
        if newspaper not in NEWSPAPERS:
            try:
                newspaper = self.guess_newspaper(newspaper)
            except NoSuchNewspaper as e:
                return False
            
        ppath = papertopath(newspaper, year, month, day, archive = self.archive)
        if os.path.isfile(ppath):
            return True
        else:
            try:
                doc = self.get(newspaper, year, month, day)
                return False
            except (NoSuchPage, NoSuchDocumentFound, NoSuchNewspaper) as e:
                return False
    
    def years_available(self, newspaper):
        if newspaper not in NEWSPAPERS:
            newspaper = self.guess_newspaper(newspaper)
        return os.listdir(os.path.join(self.archive, newspaper))
    
    def months_available(self, newspaper, year):
        if newspaper not in NEWSPAPERS:
            newspaper = self.guess_newspaper(newspaper)
        return list(set([x[:2] for x in os.listdir(os.path.join(self.archive, newspaper, year))]))
    
    def days_available(self, newspaper, year, month):
        if newspaper not in NEWSPAPERS:
            newspaper = self.guess_newspaper(newspaper)
        base_path = papertopath(newspaper, year, archive = self.archive)
        return [x[3:].split(".")[0] for x in os.listdir(base_path) if x.startswith(month)]   
    
    def get(self, newspaper, year, month, day, page=None, *params, **otherkwparams):
        doc = {}
        if newspaper not in NEWSPAPERS:
            newspaper = self.guess_newspaper(newspaper)
        cname = self._cachename(newspaper, year, month, day)
        if cname in self._cachelist:
            doc = self._cache[cname]
        else:
            ppath = papertopath(newspaper, year, month, day, archive = self.archive)
            if os.path.exists(ppath):
                with open(ppath, "r") as jd:
                    basedoc = json.load(jd)
                    self._addtocache(doc, newspaper, year, month, day)
                    for item in basedoc:
                        try:
                            docpage, article = item.split("_")
                            if docpage not in doc:
                                doc[docpage] = {}
                            doc[docpage][article] = basedoc[item]
                        except ValueError as e:
                            print(newspaper, year, month, day)
                            print(item, basedoc.keys())
                            print(ppath)
                            raise e
            else:
                raise NoSuchDocumentFound()
        if page != None and page != "":
            if len(page) != 4 or isinstance(page, int):
                page = "{0:04d}".format(int(page))
            if page in doc:
                return doc[page]
            else:
                raise NoSuchPage()
        return doc
    
    def all_available_newspaper_dates(self, newspaper, daterange = [1798, 1901]):
        if newspaper not in NEWSPAPERS:
            newspaper = self.guess_newspaper(newspaper)
        ydx = daterange[1] - daterange[0]
        for year in sorted(self.years_available(newspaper)):
            if 0 <= (int(year) - daterange[0]) < ydx:
                for month in sorted(self.months_available(newspaper, year)):
                    for day in sorted(self.days_available(newspaper, year, month)):
                        yield {'newspaper': newspaper, 
                               'year': year,
                               'month': month,
                               'day': day}
                    
    def all_available_newspapers(self, newspapers = NEWSPAPERS, daterange = [1798, 1901]):
        for newspaper in sorted(NEWSPAPERS):
            if newspaper in newspapers:
                for ref in self.all_available_newspaper_dates(newspaper, daterange):
                    yield ref

def get_weighted_list():
    n = NewspaperArchive()
    weighted_newspapers = []
    for newspaper in NEWSPAPERS:
        try:
            numb = int(len(n.years_available(newspaper)) / 10.0)
            if numb < 1: 
                numb = 1
            weighted_newspapers.extend([newspaper] * numb)
        except FileNotFoundError as e:
            ...
    return weighted_newspapers

WEIGHTED_NEWSPAPERS = get_weighted_list()

