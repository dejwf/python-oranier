#clear class for CRU(D) easy5 -> magento migration
import MySQLdb
import cPickle
class CONT:pass

class DBQuery:
    def __init__(self,conn,msql):
        self.cursor = conn.cursor()
        self.cursor.execute(msql)
        self.dlist=self.cursor.description
    def fetchone(self):
        vt=self.cursor.fetchone()
        ret=CONT()
        i=0
        for tup in self.dlist:
            (fn,tp) =tup[:2]
            fn=fn.lower()
            fn=fn.replace(" ","_")
            fn=fn.replace("(","_")
            fn=fn.replace(")","_")
            setattr(ret,fn,vt[i])
            i+=1
        return ret
    def getAll(self):
        ret=True
        while ret:
            try:
                ret=self.fetchone()
            except:
                ret=None
            if ret: yield ret
             
class easy5DB:
    u"Reading from Easy5 DB"
    def __init__(self, DBtype):
        self.charset = "utf8"
        self.DBtype = DBtype  
        if DBtype == "KT":
            self.host = "sql57.your-server.de"
            self.user = "netmark2011_r"
            self.pwd = "K0chbuch_r"
            self.db = "oraniekt"
        if DBtype == "HT":
            self.host = "sql57.your-server.de"
            self.user = 'netmark2010_r'
            self.pwd = "N0_chance_Man"
            self.db = 'oranierht'
        if DBtype == "stammdaten":
            self.host = "sql55.your-server.de"
            self.user = "oranie_13_r"
            self.pwd = "R_fuer_0R"
            self.db = "stammdaten_oranier"
    
    def read(self,command): #command example: "SELECT * FROM dunstabzug_text_de"
        conn = MySQLdb.connect(host=self.host, user=self.user,passwd=self.pwd,db=self.db,charset=self.charset)
        container = []
        for o in DBQuery(conn,command).getAll():
            container.append(o)
        return container
    
    def name(self):
        return self.db
    
    def dbAndTab(self,tabname):
        return self.db + "." + tabname 
    
    def prima(self,suffix):
        if "merkmal" in suffix:#works for both hauptmerkmale and merkmale
            return "hauptmerkmale"
        if "leistung" in suffix:
            return "leistung"
        if "farbe" in suffix:
            return "farbe"
        if "zubehoer" in suffix:
            return "zubehoer"
        else:
            return suffix
        
    def secunda(self,suffix):
        if "merkmal" in suffix:#works for both hauptmerkmale and merkmale
            return "hauptmerkmal"
        if "leistung" in suffix:
            return "leistung"
        if "farbe" in suffix:
            return "farbe"
        if "zubehoer" in suffix:
            return "zubehoer"   
        else:
            return suffix
        
    
    def tercia(self,tabname,suffix):
        if "farbe" in suffix:
            return suffix
        if ("dunstabzug" in tabname) and ("leistung" in suffix):
            return "leistung"
        if "dunstabzug" in tabname:
            return "merkmal"
        if ("zubehoer" in tabname) or ("ht" in self.db):# or self.DBtype == "HT":
            return "merkmal"
        else:
            return suffix
    
    def quatro(self,tabname,suffix):
        if self.DBtype == "HT":
            if "dunstabzug" in tabname:
                return tabname
            if "einbau" in tabname:
                return tabname
            if "kombi" in tabname:
                return tabname
            if "kombi" in tabname:
                return "einbau"
            if "mikro" in tabname:
                return "einbau"
            else:
                return "geraet"
        else:#KT
            if ("zubehoer" in tabname ) and ("hauptmerkmal" in suffix):
                return "geraet"
            if suffix == "leistung":
                return suffix
            if ("farbe" in suffix) and ("dunstabzug" or "einbau" or "kochfeld" or "kombi" or "kombikochfeld" or "kuehl" or "mikro" or "spuel" or "stand" in tabname):
                return "farbe" 
            if "dunstabzug" or "einbau" or "kochfeld" or "kombi" or "kombikochfeld" or "kuehl" or "mikro" or "spuel" or "stand" in tabname:
                return "geraet" 
            return tabname
        
    def hauptOrMerkmal(self,column = None):
        if self.DBtype == "KT":
            if column:
                return "hauptmerkmal"
            return "merkmal"
        else:
            if column:
                return "merkmal"
            return "hauptmerkmal"
    
    
class magentoProd:
    #u"manipulating magento via soap API"
    def __init__(self, soap, sessionId):
        self.soap = soap
        self.sessionId = sessionId
        pass
    
    def create(self):
        pass
    
    def update(self):
        pass
    
    def read(self):
        pass
    
    def readAll(self):
        #catalogProductList(sid)
        return self.soap.service.catalogProductList(self.sessionID)
    
    #one of the methods will be gone, when is clear, what is parent and what is child
    def childOf(self,parent,child,relation):
        #relation = "related" || "grouped"
        self.soap.service.catalogProductLinkAssign(self.sessionId ,relation ,child, parent)
        print parent,"is parent of", child
        
    #one of the methods will be gone, when is clear, what is parent and what is child
    def parentOf(self,parent,child,relation):
        #relation = "related" || "grouped"
        self.soap.service.catalogProductLinkAssign(self.sessionId ,relation ,parent, child)
        print parent,"is parent of", child
    
class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'

    def disable(self):
        self.HEADER = ''
        self.OKBLUE = ''
        self.OKGREEN = ''
        self.WARNING = ''
        self.FAIL = ''
        self.ENDC = ''    
