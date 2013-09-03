# -*- coding: utf-8 -*-
# the line above is for compilation!(http://www.evanjones.ca/python-utf8.html)
#
# The complete refilling of magento DB is currently divided into 10 steps:
#
#     1) make initial filling of DB, where minimalistic objects are created with this function - 
# loop_Thru_Tabs(createProducts); very important is the 1st parameter, it is 
# acctuall function name in which the creation process is done. The new object has:
#    website_ids,name,description,short_description,status and visibility
# status is constatnt setted to "1" (string!) and visibility is mostly setted to string "1" (not visible) - exceptions
# are accessories (zubehoer), which are setted to "4". The visibility is a flag saying, if product is searchable
# and displayable in frontend.
#    
#     2) in next step we update products categories with this function - 
# loop_Thru_Tabs(updateItemsCat); very important is the parameter - function.
# It is good to consult, if new categories have been created. In case of category(ies) change update categoryList
# within the function
#
# TODO: DEV note - functions createProducts AND updateItemsCat could be merged together! 
#    
#    3) It is time to update attribute options. Very important are the aaa_bestellnummern_ht/kt. 
# This SHOULD already be up-to-date, but it is better to run it once. 
#        loop_Thru_Tabs(expandAttributesOptions,["aaa_bestellnummern_kt","_bestnr"])
#        loop_Thru_Tabs(expandAttributesOptions,["aaa_bestellnummern_ht","_bestnr"])
#        loop_Thru_Tabs(expandAttributesOptions,["aaa_merkmale_kt","_hauptmerkmale"])
#        loop_Thru_Tabs(expandAttributesOptions,["aaa_merkmale_ht","_merkmale"])
#        loop_Thru_Tabs(expandAttributesOptions,["aaa_farben_kt","farbe"])
#        loop_Thru_Tabs(expandAttributesOptions,["aaa_farben_ht","farbe"])
#        loop_Thru_Tabs(expandAttributesOptions,["aaa_leistungsmerkmale_kt","leistung"])
#  
#
#    4) Update products w/ additional attributes.
#        loop_Thru_Tabs(updateAdditionalAttrOfProduct,["aaa_bestellnummern_kt","bestnr"])
#        loop_Thru_Tabs(updateAdditionalAttrOfProduct,["aaa_bestellnummern_ht","bestnr"])
#        loop_Thru_Tabs(updateAdditionalAttrOfProduct,["aaa_merkmale_kt","hauptmerkmale"])
#        loop_Thru_Tabs(updateAdditionalAttrOfProduct,["aaa_merkmale_ht","merkmale"])
#        loop_Thru_Tabs(updateAdditionalAttrOfProduct,["aaa_farben_kt","farbe"])
#        loop_Thru_Tabs(updateAdditionalAttrOfProduct,["aaa_farben_ht","farbe"])
#        loop_Thru_Tabs(updateAdditionalAttrOfProduct,["aaa_leistungsmerkmale_kt","leistung"])
#
#
#    5)Let's create parent products for all the orphans...
#        createParentProd()
#
#    6) Now is time to expand the parent products with children's attributes.
#        updateParentsWithChildrenAttribs()
#
#
#    7) Now is time to expand the parent products with some pictures.
#        ....no current function. Re-adjustment of this should do the job
#        loop_Thru_Tabs(updateProductsPics,[c.service.catalogProductList(sid)])
#
#    8) Link products with accessories
#        loop_Thru_Tabs(linkProductsWithAccessories)
#
#    9) Update prices. 
#         If not necessary, make prices only for child/simple products
#        updatePrices()
#
#    10) Assign Related products (zubehoer) To Parents
#        until now, the related products are linked only with child/simple - therefore
#        the relation are invisible at frontend. Function propagates the linkage for parent prods
#        assignRelatedToParents()
#
from suds.client import Client
import xlrd
#from sys import exit
from datetime import datetime as time#class for time info/manipulation dateime.now()
from HTMLParser import HTMLParser
from magento import easy5DB
import cPickle as pickle

class CONT:pass

oranierDB = CONT()
oranierDB.HT = ["gaskamin","gasheiz","kachelofen","kamineinsatz","kaminofen","kaminwasser","komplettkamine","pelletofen","zubehoer"]#listOfHeatTechnic
oranierDB.KT = ["dunstabzug","einbau","kochfeld","kombi","kombikochfeld","kuehl","mikro","spuel","stand","zubehoer"]#,listOfKitchenTechnic

class MLStripper(HTMLParser):
    def __init__(self):
        self.reset()
        self.fed = []
    def handle_data(self, d):
        self.fed.append(d)
    def get_data(self):
        return ''.join(self.fed)
    
if True:
    print time.now(),"Logging in...",
    HTTPHOST="http://netmark5.web11.hucke.net"
    c = Client(HTTPHOST+"/index.php/api/v2_soap/?wsdl")
    sid = c.service.login('soapadmin', 'aslk98swk')
    print "ok."

def updateProdCat(prodsku,websites,categories):
#===============================================================================
# updates category and website of product 
#===============================================================================
    catalogProductCreateEntity = {"categories": categories,"websites": websites}
    c.service.catalogProductUpdate(sid,prodsku,catalogProductCreateEntity,None,"sku")
    
def isAccessory(tabname):
    #hard code set to "" / 1 - not visible/ 4 - visible / make it 4  for zubehoer
    if tabname == "zubehoer":return "4"
    else:return "1"

def decomposer(string):
    ################################################
    # removes / _ . from a string and returns it ##
    ##############################################
    obj = string.replace("/"," ").replace("_"," ").replace("."," ")
    obj = obj.split()
    for part in obj:
        if len(part) > 5:
            answer = part
            break 
    return answer

def strip_tags(html):
    #######################################################################
    # removes all html tags from a string and returns the edited string ##
    #####################################################################
    s = MLStripper()
    s.feed(html)
    return s.get_data()

def remove_funkySignes(string):
    ##############################################################
    # removes  \r\n from string and returns the edited string ##
    ############################################################
    if string == None:return None
    obj = string.replace("","").replace("\r\n","")
    return obj

def parentOrChild(string,length):
    ##############################################################################
    # returns "like" or "=" to string. Used for search with sql script/command ##
    ############################################################################
    if length == "configurable":
        return 'like "'+string.split(" ")[0]+ ' %%"'
    else: return '= "'+string+'"'

def prepareContent(imageName,DB,imageType = None):
    ##############################################
    # fishes,prepares and returns image object ##
    ############################################
    if imageType:imageTypes=[imageType]
    else:imageTypes=None
    try:
        content = {
        'content' : open("C:/Users/Dawe/Desktop/"+DB.lower()+"-images/" + imageName, "rb").read().encode("base64"),
        'mime' : "image/jpeg",'name' : imageName.split(".")[0]  }
        data = {'types' : imageTypes,   #not required field
                'file' : content,
                "exclude":0}
    except Exception:data = False #no picture in the folder 
    return data

def loopThruTabs(function,params=None,dbs=None):
    ###################################################
    # a general loop for manipulation with products ##
    #################################################
    #print "WARNING!!!RUNS ONLY stand_* TABLES! \n FOR FULL RUN ALTER THE loopThruTabs()"
    if not dbs:
        if not params:#podminka, ktera udela komplet import pro "stand" tabulku
            for tabname in oranierDB.HT:
                #if tabname == "stand":
                    function("HT",tabname)
            for tabname in oranierDB.KT:
                #if tabname == "stand":
                    function("KT",tabname)
        else:
            for tabname in oranierDB.HT:
                #if tabname == "stand":
                    function("HT",tabname,*params)
            for tabname in oranierDB.KT:
                #if tabname == "stand":
                    function("KT",tabname,*params)
    else:
        if not params:
            if "HT" in dbs:
                for tabname in oranierDB.HT:
                    #if tabname == "stand":
                        function("HT",tabname)
            if "KT" in dbs:
                for tabname in oranierDB.KT:
                    #if tabname == "stand":
                        function("KT",tabname)
        else:
            if "HT" in dbs:
                for tabname in oranierDB.HT:
                    #if tabname == "stand":
                        function("HT",tabname,*params)
            if "KT" in dbs:
                for tabname in oranierDB.KT:
                    #if tabname == "stand":
                        function("KT",tabname,*params)
    

def cutOffPicturesUnderlineVersion():
    #
    # cuts off the underline "_" character form picture file name
    # e.g. from /3/9/3999012798baa19e5be5539e3efda328_117.jpg
    # ==> 3999012798baa19e5be5539e3efda328.jpg
    # 
    # no effect...19/3/13
    print "reading DB...",
    DBList=c.service.catalogProductList(sid)
    print "done"
    for product in DBList:
        if product.type == "configurable":
                print "reading pictures of ",product.sku ,"...",time.now(),
                picList = c.service.catalogProductAttributeMediaList(sid, product.sku ,None,"sku")
                print "done"
                for pic in picList:
                    if len(pic.types) > 0:
                        catalogProductImageFileEntity = {"name":decomposer(pic.file)}
                        catalogProductAttributeMediaCreateEntity = {"file":catalogProductImageFileEntity
                                                                      #"label": Product image label
                                                                      #"position": Product image position
                                                                      #"types": Array of types
                                                                      #"exclude":    Defines whether the image will associate only to one of three image types
                                                                      ##"remove":Image remove flag 
                                                                      }
                        try:
                            resp=c.service.catalogProductAttributeMediaUpdate(sid,product.sku,pic.file,catalogProductAttributeMediaCreateEntity,None,"sku")
                            print "call to update success? => ",resp
                        except Exception,e:
                            print e

def cleanParentsPictures():
    ###############################################################################################
    # deletes all pictures from parent product, which have no type (small,base,thumb) specified ##
    #############################################################################################
    print "reading DB...",
    DBList=c.service.catalogProductList(sid)
    print "done"
    for cnt,product in enumerate(DBList):
        if product.type == "configurable":
                print cnt,"/",len(DBList),"reading pictures...",time.now(),
                picList = c.service.catalogProductAttributeMediaList(sid, product.sku ,None,"sku")
                print "done"
                for pic in picList:
                    if len(pic.types) < 1:
                        try:
                            resp = c.service.catalogProductAttributeMediaRemove(sid,product.sku ,pic.file,"sku")
                            print "call to delete success? => ",resp
                        except Exception,e:
                            print e

def distributePictures(pic,sku,DB,imageType):
    #################################################
    # uploads pictures with a proper picture type ##
    ###############################################
    if pic != None:
        data = prepareContent(pic,DB,imageType)
        if data != False:
            try:
                resp=c.service.catalogProductAttributeMediaCreate(sid,sku,data,None,"sku")
                print sku,imageType," inserted under ID ", resp
            except Exception,e:print  sku,";",e

def updateProductsPics(DB,tabname , DBList):
    ####################################################
    # searches easy5 database and processes pictures ##
    ##################################################
    # prevent of filling same pictures with the pushed [list]
    pushed=[]
    for cnt,product in enumerate(DBList):
        # pushed=[] # alternate position
        if len(product.sku) > 5:continue #runs just parents
        sql_command=("SELECT " + tabname + "_bestnr.bestnr, "+ tabname + "_bestnr.text AS name, "+ 
                     tabname + ".bild AS small_image, "+ tabname + ".bild2 AS image, "+ 
                     tabname + "_bild.bild AS gallery, " + tabname + "_bild.text AS description "+ " FROM "+
                     easy5DB(DB).name() + '.' + tabname + '_bestnr LEFT JOIN ' +  easy5DB(DB).name() + '.' + tabname + ' ON ' +
                     easy5DB(DB).name() + '.' + tabname + '_bestnr.id_geraet = '  + easy5DB(DB).name() + '.' + tabname + '.id LEFT JOIN '+   
                     easy5DB(DB).name() + '.' + tabname + '_bild ON ' + easy5DB(DB).name() + '.' + tabname + '_bild.id_top = ' + 
                     easy5DB(DB).name() + '.' + tabname + '.id where bestnr ' + parentOrChild(product.sku,product.type) )
        ProdPics = easy5DB(DB).read(sql_command)
        if len(ProdPics) < 1:continue
        for picSet in ProdPics:
            #here check if picture is already in pushed [list]; if not proceed
            if picSet.gallery not in pushed:
                distributePictures(picSet.gallery,product.sku,DB,"gallery")
            if picSet.image not in pushed:
                distributePictures(picSet.image,product.sku,DB,"image") 
            if picSet.small_image not in pushed:
                distributePictures(picSet.small_image,product.sku,DB,"small_image")
            #add picture to pushed [list]
            pushed.append(picSet.gallery)
            pushed.append(picSet.small_image)
            pushed.append(picSet.image)
#            distributePictures(picSet,product.sku,DB,imageType)
        print cnt,"/",len(DBList), product.sku
    print tabname , " done..."

def uploadDealersAndAddresses():
    ############################################
    #                                        ##
    ##########################################
    dealers = easy5DB("stammdaten").read("SELECT * FROM stammdaten_oranier.user")
#    cnt = 0
#    for easy1 in dealers:
#        cnt += 1 
#        if easy1.name_firma1 == "Hees Sanitär GmbH":
#            print cnt
    for cnt,easy1 in enumerate(dealers):
        #if cnt < 9165:continue
        print cnt,"/",len(dealers)
        if easy1.quelle == "":
            website_id = "0"
            group_id = "1"
            #store_id = "1"
        if not hasattr(easy1,"quelle"):
            website_id = "0"
            group_id = "1"
            #store_id = "1"
        if easy1.quelle == "HT":
            website_id = "1"
            group_id = "4"
        if easy1.quelle == "KT":
            website_id = "3"
            group_id = "5"
        if easy1.lkz == "A":countryCode = "AT"
        if easy1.lkz == "D":countryCode = "DE"
        newc={  'email' : easy1.email_user, 
            'firstname' : 'Firma', 
            'lastname' : easy1.name_firma1, 
            'password' : easy1.deb_nr, 
            'website_id' : website_id , 
            'group_id' : group_id,
              ##'store_id' : 1 # very probably is the number of customer 
              }
        streets = [easy1.strasse]
        addressdata = {
            "city":easy1.ort,
            "country_id": countryCode, # DE,AT
            "firstname":'Firma', 
            "lastname":easy1.name_firma1,
            "postcode":easy1.plz,
            "street":streets,
            "telephone":"no-tel-in-db",#str(easy1.telefon),
            "is_default_billing": True,
            "is_default_shipping": True           
                    }
        try:
            customerID=c.service.customerCustomerCreate(sid,newc)
            print "DONE: customer id=>", customerID, 
            resp = c.service.customerAddressCreate(sid,customerID,addressdata)
            print "address ID =>",resp
        except Exception,e:print e
             
def customerAddressUpdate():
    ############################################
    #                                        ##
    ##########################################
    cnta = 0
    sql_command=("SELECT * FROM stammdaten_oranier.haendler")
    easy5Customers =  easy5DB("stammdaten").read(sql_command)   
    magentoCustomers = c.service.customerCustomerList(sid)
    print "magento customers loaded" 
    for easy1 in easy5Customers:
        for mage1 in magentoCustomers:
            if easy1.name1 == mage1.lastname:
                cnta += 1 
                if mage1.customer_id < 1286:continue
                if easy1.lkz == "A":
                    countryCode = "AT"
                if easy1.lkz == "D":
                    countryCode = "DE"
                    streets = [easy1.strasse]
                customerAddressEntityCreate = {
                    "city":easy1.ort,
                    "country_id": countryCode, # DE,AT
                    "firstname":mage1.firstname, 
                    "lastname":mage1.lastname,
                    "postcode":easy1.plz,
                    "street":streets,
                    "telephone":str(easy1.telefon),
                    "is_default_billing": True,
                    "is_default_shipping": True
                    ##"prefix"#"suffix"#"company":easy1.name1,#"region"#"region_id":,#"middlename"#"fax": easy1.fax,
                                   } 
                try:
                    c.service.customerAddressCreate(sid,mage1.customer_id,customerAddressEntityCreate)
                    print cnta, mage1.customer_id, mage1.firstname, mage1.lastname
                except Exception,e:
                    print e
    
def setBestellnummernToChildren():
    # prirad aaa_bestellnummern_xx option ke spravenmu sku 
    # (tj jmeno produktu a option se musi shodovat), pote prirad atribut decek rodicum
    #
    # prepares an attribute's option for sku
    #
    print "reading magento DB....",
    DBList=c.service.catalogProductList(sid)
    bestKT=c.service.catalogProductAttributeInfo(sid,"aaa_bestellnummern_kt")
    bestHT=c.service.catalogProductAttributeInfo(sid,"aaa_bestellnummern_ht")
    print "done"
    parents,children = [],[]
    for types in DBList:
        if types.type == "simple":children.append(types)
        if types.type == "configurable":parents.append(types)
    for child in children:
        print "\nlooking for", child.sku , "in table",  
        for tabname in oranierDB.HT:
            prepareProductAndUpdateItWithAdditionalAttributes("HT",bestHT,tabname,child)
        for tabname in oranierDB.KT:
            prepareProductAndUpdateItWithAdditionalAttributes("KT",bestKT,tabname,child)

def prepareProductAndUpdateItWithAdditionalAttributes(DB,best,tabname,child):
    ##########################################
    # proceeds the sku's option assignment ##
    ########################################
    print tabname ,
    sql = 'SELECT * FROM '+easy5DB(DB).name()+'.'+tabname+'_bestnr where bestnr = "'+ child.sku +'"'
    content = easy5DB(DB).read(sql)
    if len(content) < 1:return#continue
    print len(content) , "options"
    options = []
    for one in content:
        if one.bestnr == child.sku:
            for mem in best.options:
                one.text = strip_tags(one.text)
                if one.text != mem.label:continue
                options.append(str(mem.value))     
                break#could be outcommented?
    options = list(set(options)) #zbavi list duplicitnich hodnot
    options = ",".join(options)  #prevede list do stringu
    if DB == "HT":attributesID = "aaa_bestellnummern_ht"
    if DB == "KT":attributesID = "aaa_bestellnummern_kt"
    resp = updateProdAdditionalAttr(child.sku,attributesID,options)
    print resp.sku, resp.attribs      
    
def updateItemsCat(DB,tabname):
    #######################################################
    # sorts product objects to categories and web-sites ##
    #####################################################
    print "reading DBs"
    sql_command=("SELECT * FROM "+
                 easy5DB(DB).name()+"."+tabname+"_bestnr left join "+
                 easy5DB(DB).name()+"."+tabname+" on "+
                 easy5DB(DB).name()+"."+tabname+"_bestnr.id_geraet = "+
                 easy5DB(DB).name()+"."+tabname+".id")
    joined =  easy5DB(DB).read(sql_command)      
    DBList=c.service.catalogProductList (sid)
    categoryList={"gaskamin":125,"gasheiz":126,"kachelofen":120,"kamineinsatz":124,"kaminofen":120,
                  "kaminwasser":121,"komplettkamine":122,"pelletofen":123,"dunstabzug":40,"einbau":56,
                  "kochfeld":67,"kombi":67,"stand":168,"kombikochfeld":67,"kuehl":98,"mikro":86,"spuel":91}
    categories=[]
    categories.append(categoryList.get(tabname))
    websites=[]
    if DB == "KT":
        if tabname == "zubehoer":
            categories.append(162)
        categories.append(7)
        categories.append(9)
        websites.append("3")
        
    if DB == "HT":
        if tabname == "zubehoer":
            categories.append(161)
        categories.append(2)
        categories.append(4)
        websites.append("1")
    print categoryList.get(tabname)
    cnt = 0
    for easy5one in joined:
        for mageMem in DBList:    
            if str(easy5one.bestnr) == str(mageMem.sku):
                cnt += 1 
                updateProdCat(easy5one.bestnr,websites,categories)
                print easy5one.bestnr, " is in category " ,tabname,
                print " loop # ", cnt 

def updateProdAdditionalAttr(prodsku,attributesID,additAttr,check = None,others = None):
    ###################################################################
    # executes the final product's additional attribute update pump ##
    #################################################################
    adds = {"additional_attributes":[attributesID]}
    if check:
        try:
            prodinfo = c.service.catalogProductInfo(sid,prodsku, None, adds,"sku")
            if hasattr(prodinfo,"additional_attributes"):
                for one in prodinfo.additional_attributes:
                    if one.value != None: 
                        additAttr = additAttr + "," + one.value
        except Exception, a:
            print "fail",a , prodsku
            return
    containerObject = {"key" : attributesID,"value" : additAttr}
    containerArray = [];
    containerArray.append(containerObject);                       
    additionalAttrs1 = {"single_data" : containerArray}
    catalogProductCreateEntity = {"additional_attributes": additionalAttrs1, 
                                  "status":"1" #if product is not visible in backend, make sure the status is on
                                }
    if others:
        #there was a plan for something, but i do not know anymore
        catalogProductCreateEntity.items(others.key,others.value)
    try:
        resp = CONT()
        resp.soap=c.service.catalogProductUpdate(sid,prodsku,catalogProductCreateEntity,None,"sku")
        resp.sku = prodsku
        resp.attribs = additAttr
        return resp 
    except Exception, e:
        print "failEnd",e   

def updateAdditionalAttrOfProduct(DB,tabname,attributeName,suffix): 
#===========================================================================
# updates product object with an option of specific additional attribute 
#===========================================================================
#skip these tables
#    if "zubehoer" not in tabname:return
#    if DB=="HT":return
#        if "kamineinsatz" or "kachelofen" or "gasheiz" or "gaskamin" in tabname:return
#    if DB=="KT":return
#    if "dunstabzug" in tabname:return #"dunstabzug","einbau","kochfeld","kombi","kombikochfeld","kuehl","mikro","spuel","stand","zubehoer"
    #if tabname != "stand":return
    #if (tabname != "zubehoer"):return
#    if "dunstabzug" in tabname:return
#    if "einbau" in tabname:return
#    if "kuehl" in tabname:return
#    if "spuel" in tabname:return
#    if "stand" in tabname:return
    print attributeName,tabname, "in", DB
    if ("farbe" in suffix): 
        if ("kochfeld" in tabname) or ("kuehl" in tabname ) or ("spuel" in tabname):
            print "makes no sense to fill it for",tabname,"table set"
            return
    if tabname == "zubehoer":suffix = "hauptmerkmal"
    tbs  =  easy5DB(DB)
    command = ("SELECT * FROM "  + tbs.db+ "." + tabname + "_bestnr")
    objectsDB = tbs.read(command)
    for loopnr, uniqueBest in enumerate(objectsDB,1):
        #print loopnr, "/", len(objectsDB)
        sku = str(uniqueBest.bestnr)     
        #if "9926" not in sku:continue#debugg line...#9926 06
        if "bestellnummern" in attributeName:  
            sql_command=("SELECT "+
                        tbs.db +"."+tabname +"_bestnr.text as name, " +
                        tbs.db +"."+tabname +"_bestnr.bestnr as bestnr " + 
                        " FROM "+
                        tbs.db +"."+tabname +"_bestnr " +
                        ' where bestnr = "' + sku + '"'  
                    )
        elif "leistung" in attributeName:#tbs.dbAndTab(tabname) 
            sql_command=("SELECT "+
                         tbs.dbAndTab(tabname)+"_bestnr.bestnr, leistung_text_de.name  "+
                         "FROM "+tbs.dbAndTab(tabname)+"_bestnr " + 
                         "left join "+tbs.dbAndTab(tabname)+"_leistung on "+ 
                         tbs.dbAndTab(tabname)+"_bestnr.id_geraet = " +
                         tbs.dbAndTab(tabname)+"_leistung.id_geraet " + 
                         "left join  "+tbs.db +".leistung_text_de on " +
                         tbs.db +".leistung_text_de.id = "+
                         tbs.dbAndTab(tabname)+"_leistung.id_leistung " + 
                         ' where bestnr = "' + sku + '"' ) #where bestnr = "9926 06"
            if tabname==("kochfeld" or "kombikochfeld" or "mikro"):
                sql_command=("SELECT "+
                         tbs.dbAndTab(tabname)+"_bestnr.bestnr, leistung.name  "+
                         "FROM "+tbs.dbAndTab(tabname)+"_bestnr " + 
                         "left join "+tbs.dbAndTab(tabname)+"_leistung on "+ 
                         tbs.dbAndTab(tabname)+"_bestnr.id_geraet = " +
                         tbs.dbAndTab(tabname)+"_leistung.id_geraet " + 
                         "left join  "+tbs.db +".leistung on " +
                         tbs.db +".leistung.id = "+
                         tbs.dbAndTab(tabname)+"_leistung.id_leistung " + 
                         ' where bestnr = "' + sku + '"' ) 
        else: 
            sql_command=("SELECT "+
                    tbs.db+"."+tabname+ "_bestnr.bestnr, "+tbs.prima(suffix)+"_text_de.name" +
                    " FROM "+  
                    tbs.db+ '.' + tabname + "_" + suffix +
                    ' left join ' +                   
                    tbs.db+ '.' + tabname + '_bestnr on ' +                   
                    tabname + "_" + suffix + '.id_'+tbs.quatro(tabname,suffix)+' = '  + #geraet||dunstabzug       
                    tabname + '_bestnr' +'.id_geraet' + 
                    ' left join '+    
                    tbs.db+ '.'+tbs.prima(suffix)+'_text_de on ' +
                                                            #@- hauptmerkmal
                    tbs.prima(suffix) +'_text_de.id_'+tbs.secunda(suffix)+' = ' +
                                                    # merkmal || farbe || @- merkmal 
                    tabname + "_" + suffix +'.id_' + tbs.tercia(tabname,suffix) +
                    ' where bestnr = "' + sku + '"')
        try:
            easy5attribs  =  easy5DB(DB).read(sql_command)
        except Exception, e:
            print e 
            continue
        if len(easy5attribs) < 1:
            print uniqueBest.bestnr,"NONE easy5attribs"
            continue
#        if "9926" in uniqueBest.bestnr:#9926 06
#            pass
#            #print uniqueBest.bestnr,"already filled - Outcomment me for full functionality"
#        else:
#            continue
        try:
            attroptions = c.service.catalogProductAttributeOptions (sid,attributeName)
        except Exception,e:
            print e
            continue
        attributeString = []
        for mix in easy5attribs:
            for option in attroptions:
                if option.label != mix.name:continue
                if option.label == None:continue
                attributeString.append(option.value)    
        if len(attributeString) < 1:
            print uniqueBest.bestnr, "has no attributes"
            continue
        attributeString= list(set(attributeString)) #removes duplicit values
        attributeString = ",".join(attributeString) #converts list to "," separated string  
        if "6357.19" in str(mix.bestnr):mix.bestnr = "6357 19"
        if "6357.35" in str(mix.bestnr):mix.bestnr = "6357 35" 
        try:
            resp = updateProdAdditionalAttr(str(mix.bestnr),attributeName,attributeString)
            print loopnr, resp.sku,"has:", resp.attribs
        except Exception, e:
            print e

def isAlreadyInList(attr_value,optionList):
#===========================================================================
# compares optionList with attribute.name/text; returns True if matches
#===========================================================================
    for option in optionList:
        if option.label == attr_value:
            return True
    return False
            
def expandAttributesOptions(DB,tabname,attrName,tabsuffix = None):
#===========================================================================
# creates new option for specific additional attribute
#===========================================================================
    optionList = c.service.catalogProductAttributeOptions(sid,attrName) 
    alreadyDone,label = [],[]
    if tabsuffix:suffix = tabsuffix
    #elif tabsuffix == False:suffix = ";" 
    else:suffix = "_text_de"
    command = ("SELECT * FROM "+easy5DB(DB).name()+"." +tabname+ suffix )
    easy5attribs  =  easy5DB(DB).read(command)
    if len(easy5attribs) < 1:return   
    #listName = list(set(listName)) #zbavi list duplicitnich hodnot
    #remove duplicates from list
    easy5attribs = list(set(easy5attribs)) 
    for cnt,attribute in enumerate(easy5attribs,1):
        if hasattr(attribute,"text"):attr_value = attribute.text
        if hasattr(attribute,"name"):attr_value = attribute.name
        if isAlreadyInList(attr_value,optionList):continue
        isDone = next((True for x in alreadyDone if attr_value == x),False)
        if isDone:
            continue
        print cnt ,"/", len(easy5attribs),attr_value,
        label.append({"store_id":["0"],"value":attr_value})
        data = {"label":label}
        try:
            resp=c.service.catalogProductAttributeAddOption(sid,attrName,data)
            print "successful?:" , resp
        except Exception, e:
            print e 
        alreadyDone.append(attr_value)    
        
def createParentProd():
    #===========================================================================
    # derives "parent products" from existing (simple/child) products
    #===========================================================================
    prodList = c.service.catalogProductList(sid)
    parents,created=[],[] 
    for x in prodList:
        if x.type == "simple":
            print x.sku,
            x.sku = x.sku.split(" ")[0]
            if len(x.sku)<4:
                print "too short->",x.sku
                continue
            parents.append(x)
        print
    
#    created.append("pit0001")
#    created.append("pit0002")
#    created.append("testID")
#    created.append("testID1")
    for cnt,parent in enumerate(parents,1):
        data = {
                'category_ids' : parent.category_ids,
                'website_ids' : parent.website_ids,
                'name' : parent.name,
                'status' : '1',
                'visibility' : '4', # 4 = searchable 
                }
        sku = parent.sku
        sett = parent.set
        #if cnt < 430:continue
        if next((True for i in created if str(i) == str(sku)),False):continue
        try: 
            c.service.catalogProductCreate(sid,"configurable",sett,sku,data )# No param "sku" when creating an object
            print cnt,"/", len(parents) ,": ", sku, " created"
            created.append(sku)
        except Exception,e:
            print cnt, sku, e 

def checkParentsNamesAndFillIfNecesary():
#===============================================================================
# if parent has no name but child has, assign child's name to the parent
#===============================================================================
    DBList=c.service.catalogProductList(sid)
    parents,children = [x for x in DBList if x.type == "configurable"],[x for x in DBList if x.type == "simple"]
    nonameParents = [x for x in parents if not x.name]
    for i,o in enumerate(nonameParents,1):
#        print i,o.sku#
        if ("8716" or "8739" or "8737" or "8768" or "9901" or "9866" or "9860" or "9870" or "2727" or "1937" or "1939" or "1807") in o.sku:
            pass
        for child in children:
#            if "8738" in child.sku:
#                pass
#            if len(child.sku)<=1:continue 
            if o.sku in child.sku:                
                if not child.name:continue
                print "child",child.sku,child.name
                o.name = child.name 
#                hasNameParents.append(o)
                c.service.catalogProductUpdate(sid,o.sku,{"name":o.name},None,"sku")
                break

def updateParentsWithChildrenAttribs():
#===========================================================================
# searches child products additional attributes and propagates the values to parents
#===========================================================================
    DBList=c.service.catalogProductList (sid)
    parents,children,updated = [x for x in DBList if x.type == "configurable"],[x for x in DBList if x.type == "simple"],[]
    for cnt,parent in enumerate(parents,1):
        #The 2 lines bellow is for debugging And minimazing loops
        #if cnt < 321: continue
        #if parent.sku == "8167": continue
        #a parent object is processed now on...
        print cnt,"/", len(parents),":",parent.sku
        if next((True for i in updated if str(i) == str(parent.sku)),False):continue
        myChildren = []
        for child in children:
            if parent.sku == child.sku.split(" ")[0]:
                #finds a child for the parent
                if child.website_ids[0] == "1":#ht
                    adds = {"additional_attributes":["aaa_merkmale_ht","aaa_farben_ht","aaa_bestellnummern_ht"]}
                if child.website_ids[0] == "3":#kt 
                    adds = {"additional_attributes":["aaa_leistungsmerkmale_kt","aaa_merkmale_kt","aaa_farben_kt","aaa_bestellnummern_kt"]}
                try: 
                    resp = c.service.catalogProductInfo(sid,child.sku, None, adds,"sku")
                    myChildren.append(resp)
                except Exception,e:
                    print e
        sumObj = CONT()
        sumObj.additional_attributes = []
        sumObj.description = ""
        sumObj.short_description = ""
        attribsFarben, attribsMerkmale, attribsBestnr, attribsLeistungs = [],[],[],[]
        for kid in myChildren:
            if not hasattr(kid,"additional_attributes"):
                print "check additional_attributes by,",kid.sku
                continue
            for attrs in kid.additional_attributes:
                #creating attribute values strings
                if "bestellnummern" in attrs.key:
                    if attrs.value == None:continue
                    attribsBestnr.append(attrs.value)
                    attrs.value = ",".join(list(set(attribsBestnr))) #converts list to "," separated string
            
                if "farben" in attrs.key: 
                    if attrs.value == None:continue
                    attribsFarben.append(attrs.value)
                    attrs.value = ",".join(list(set(attribsFarben))) #converts list to "," separated string
                    
                if "_merkmale" in attrs.key:
                    if attrs.value == None:continue
                    attribsMerkmale.append(attrs.value)
                    attrs.value = ",".join(list(set(attribsMerkmale))) #converts list to "," separated string
                    
                if "leistungsmerkmale" in attrs.key:
                    if attrs.value == None:continue
                    attribsLeistungs .append(attrs.value)
                    attrs.value = ",".join(list(set(attribsLeistungs ))) #converts list to "," separated string
                    
        sumObj.additional_attributes = kid.additional_attributes
        if hasattr(kid,"description"):
            sumObj.description = kid.description
        else:
            sumObj.description = "NONE"
        if hasattr(kid,"short_description"):
            sumObj.short_description = kid.short_description
        else:
            sumObj.short_description = "NONE"                     
        additionalAttrs1 = {"single_data" : kid.additional_attributes} #possibly single_data||multi_data
        catalogProductCreateEntity = {
                              "status":"1",
                              "additional_attributes":additionalAttrs1,# kid.additional_attributes,
                              "description":sumObj.description,
                              "short_description":sumObj.short_description 
                              }
        try:
            back = c.service.catalogProductUpdate(sid,parent.sku,catalogProductCreateEntity,None,"sku")
            print parent.sku, ": updated",back
            updated.append(parent.sku)
        except Exception,e:
            print parent.sku, ":", e
    pass

def linkProductsWithAccessories(DB,tabname):
#===========================================================================
# searches the connections between products and their accessories in easy5
# and recreates it in magento db                                          
#===========================================================================
    #if DB == "KT":return
    print DB,tabname,time.now()  
    sql_string =  ("SELECT "+tabname+"_bestnr.bestnr AS sku," +  
    "zubehoer.produkt_name as AccessoryDescription," +
    easy5DB(DB).name()+".zubehoer_bestnr.bestnr AS sku2" + 
    " FROM " + 
        easy5DB(DB).name()+"." + tabname +"_bestnr" + 
        " LEFT JOIN "+easy5DB(DB).name()+"."+tabname+"_zubehoer"+
            " ON " + easy5DB(DB).name()+"."+tabname+"_bestnr.id_geraet = "+
                    easy5DB(DB).name()+"."+tabname+"_zubehoer.id_geraet "
        " LEFT JOIN "+easy5DB(DB).name()+".zubehoer" + 
            " ON "+easy5DB(DB).name()+"."+tabname+"_zubehoer.id_zubehoer = " +
                easy5DB(DB).name()+".zubehoer.id"
        " LEFT JOIN "+easy5DB(DB).name()+".zubehoer_bestnr"+
            " ON zubehoer.id = zubehoer_bestnr.id_geraet;")
    easy5  =  easy5DB(DB).read(sql_string)
    for cnt,conn in enumerate(easy5,1): #conn = connection
        try:
            c.service.catalogProductLinkAssign(sid,"related",conn.sku,conn.sku2,None,"sku") #data || None
            print cnt,"/",len(easy5), " ; ",conn.sku,"related to",conn.sku2
        except Exception,e:print e, conn.sku, conn.sku2     
    pass

def createProducts(DB,tabname):
#===============================================================================
# creates a product according to easy5 DB values    
#===============================================================================
    command = ("select * from " + 
        easy5DB(DB).name()+"."+tabname+"_bestnr" + 
        " left join " + easy5DB(DB).name()+"."+tabname+ "_text_de on " +
            easy5DB(DB).name()+"."+tabname+"_bestnr.id_geraet = " + easy5DB(DB).name()+"."+tabname+ "_text_de.id_geraet" +
        " left join " + easy5DB(DB).name()+"."+tabname+" on " +
            easy5DB(DB).name()+"."+tabname+ "_text_de.id_geraet = " + easy5DB(DB).name()+"."+tabname+".id")
    prods = easy5DB(DB).read(command)
    for cnt,prod in enumerate(prods,1):
        print easy5DB(DB).name(), tabname , cnt , "/", prods.__len__(),
        if tabname == "dunstabzug" and cnt < 15:
            continue  
        if not hasattr(prod,"bestnr"):
            print prod.id
            continue
        if DB == "HT":
            set_id = [x.set_id for x in attributeSets if x.name == DB]#//9
            website_id = "1"
        if DB == "KT":
            set_id = [x.set_id for x in attributeSets if x.name == DB] #//10
            website_id = "3"
        newproduct={
            "website_ids":[website_id], 
            'name' : remove_funkySignes(prod.name), 
            'description' : remove_funkySignes(prod.ltext), 
            'short_description' : remove_funkySignes(prod.ktext), 
            'status' : "1",
            'visibility' : isAccessory(tabname)
            }
        print ",inserting...", prod.bestnr,
        try:
            mageID = c.service.catalogProductCreate(sid,"simple",set_id[0],prod.bestnr,newproduct)
            print ",done", mageID
        except Exception,e:
            print "fail"
            print e

def checkMiscSkus(DB,tabname):
#===============================================================================
# reads excel file with failed skus and tries to create them 
#===============================================================================
    wb = xlrd.open_workbook('C:\Users\Dawe\Desktop\product not exists.xlsm')
    #wb = load_workbook(filename = r'C:\Users\Dawe\Desktop\product not exists.xlsm')
    #textFile = open("C:\Users\Dawe\Desktop\_Product not exists._ 6082 28 9004 30.txt", "r")
    with open("C:\Users\Dawe\Desktop\_Product not exists._ 6082 28 9004 30.txt") as f:
        content = f.readlines()
    print DB,tabname,time.now()
    print wb
    print content
    
def updatePrices():
#===============================================================================
# updates prices of all simple products, the parent product 
# should not be affected at all                            
#===============================================================================
    products = c.service.catalogProductList(sid)
    for cnt,product in enumerate(products,1):  
        if cnt < 1251:continue
        sql_command=(
            "SELECT " + 
            "stammdaten_oranier.artikel.artikel_nr as sku,"+
            "stammdaten_oranier.artikel.vk_preis as price "+
            "FROM stammdaten_oranier.artikel "+
            ' where artikel_nr  = "' + product.sku + '"')
            #'where artikel_nr ' + parentOrChild(product.sku,product.type) )  
        outcome = easy5DB("stammdaten").read(sql_command)
        if len(outcome) < 1:continue
        try:
            c.service.catalogProductUpdate(sid,product.sku,{"price":outcome[0].price},None,"sku")
            print cnt,"/",len(products),product.sku
        except Exception,e:print product.sku,e 
    pass

#def giveMeName(name1,name2):
#    if len(name.split(" ")) > 1:
#        pass
#    else:
#        name.split(" ")[0]

def importADMs():
#===============================================================================
# imports ADM "users" and their adresses 
#===============================================================================
    outcome = easy5DB("stammdaten").read("SELECT * FROM stammdaten_oranier.adm")
    for cnt,adm in enumerate(outcome,1):
        if cnt == 1:continue  
        if cnt < 47:continue
        email = ((adm.vt_name.replace(" ", "")+"@fake.com") if adm.email == "a.rein@oranier.com" or adm.email == "schlegel@oranier.com" or adm.email == "sales@oranier.at" or adm.email == "stani@oranier.com" else adm.email)
        newc={  'email' : email.strip() ,#str(adm.email),#adm.vt_name.replace(" ", "")
            'firstname' : str(adm.vt_name), 
            'lastname' : str(adm.vt_name1), 
            'password' : "100.000", 
            'website_id' : 0 , 
            'group_id' : 6,
            #'store_id' : stid #int(adm.vt_nr) # very probably is the number of customer 
              }
        try:
            customerID=c.service.customerCustomerCreate(sid,newc)
            print "CREATED: customer id=>", customerID
        except Exception,e:
            print cnt, e, adm.vt_nr 
        if hasattr(adm,"strasse"):
            if len(adm.strasse)< 1:continue
            streets = [adm.strasse ]
            adress = zipcodes(adm.ort)
            tel = ("no-tel-in-db" if adm.vt_a_tel == "" else adm.vt_a_tel)
            addressdata = {
                "city":adress.city,
                "country_id": adress.countryCode, # FR,BE,NL,DE,AT,
                "firstname":adm.vt_name, 
                "lastname":adm.vt_name,
                "postcode":adress.zip,
                "street":streets,
                "telephone":tel,#adm.vt_a_tel,#str(easy1.telefon),
                "is_default_billing": True,
                "is_default_shipping": True           
                    }
            try:
                resp = c.service.customerAddressCreate(sid,customerID,addressdata)            
            except Exception,e:
                print cnt, e, adm.vt_nr
            print "DONE: customer id=>", customerID, "real address=>", resp
        #end of if hasattr(adm,"strasse")
        """
        #creat4e aaa_adm street
        streets = ["aaa_adm"]
        addressdata = {
            "city":adress.city,
            "country_id": adress.countryCode, # FR,BE,NL,DE,AT,
            "firstname":adm.vt_name, 
            "lastname":adm.vt_name,
            "postcode":adress.zip,
            "street":streets,
            "telephone":adm.vt_a_tel,#str(easy1.telefon),
            "is_default_billing": False,
            "is_default_shipping": False           
                }
        resp = c.service.customerAddressCreate(sid,customerID,addressdata)
        print "DONE: customer id=>", customerID, "adm info 'address'=>", resp
        """
def zipcodes(zipcode):
#===============================================================================
# resorts and returns adjusted ADM adresses. Works with importADMs() only 
#===============================================================================
    if zipcode[0] == "A":
        Anfang = [x for x in zipcode[:8].replace("-", " ", 1).split(" ") if len(x) > 0]
        AEnde =  zipcode[8:]
        if len(Anfang) > 2: AEnde = (Anfang[2] + zipcode[8:])
        adress = CONT()
        adress.zip = Anfang[1].strip()
        adress.countryCode = "AT"
        adress.city =  AEnde.strip() 
        return adress
        #print adress.zip,adress.city,adress.countryCode
    elif zipcode[0] == "N":
        if zipcode == "NL-4601 ZA Bergen op Zoom":
            adress = CONT()
            adress.zip = "4601 ZA"
            adress.countryCode = "NL"
            adress.city =  "Bergen op Zoom"
            return adress
            #print adress.zip,adress.city,adress.countryCode
        else:print "checkMe!",zipcode
    elif zipcode[0] == "B":
        Anfang = [x for x in zipcode[:8].replace("-", " ", 1).split(" ") if len(x) > 0]
        AEnde =  zipcode[8:]
        if len(Anfang) > 2:AEnde = (Anfang[2] + zipcode[8:])
        adress = CONT()
        adress.zip = Anfang[1].strip()
        adress.countryCode = "BE"
        adress.city =  AEnde.strip()
        return adress
        #print adress.zip,adress.city,adress.countryCode
    elif zipcode[0] == "F":
        Anfang = [x for x in zipcode[:9].replace("-", " ", 1).split(" ") if len(x) > 0]
        AEnde =  zipcode[9:]
        if len(Anfang) > 2: AEnde = (Anfang[2] + zipcode[9:]) 
        adress = CONT()
        adress.zip = Anfang[1].strip()
        adress.countryCode = "FR"
        adress.city =  AEnde.upper().strip() 
        return adress
        #print adress.zip,adress.city,adress.countryCode
    else:
        adress = CONT()
        adress.zip = zipcode.split(" ")[0].strip()
        adress.countryCode = "DE"
        adress.city =  zipcode.replace(adress.zip,"").strip()
        return adress
        #print adress.zip,adress.city,adress.countryCode
        
def processUsersByAMDsIDs(pos,major,easy5User ):
    print major[0]
#        for x in easy5Users:
#            #print x.email_user, major.email
#            if x.email_user in major.email:
#                print ">-match->",x.email_user
    #admId = [x for x in easy5Users if x.email_user in major.email]
#        admoObj = [x for x in easy5Users if x.email_user in major.email]
#        print len(admId)
#        if len(admId) < 1:continue
        
#        print major.firstname
#        print major.lastname
#        print streets
#        print major.firstname
        #[0] = email,[09] = firstname, [12] = lastname
    #print len(major[12])
    if len(major[9]) <= 1:
        major[9] = easy5User.email_user.split("@")[0]
    if len(major[12]) <= 1:
        major[12] = easy5User.email_user.split("@")[0]
    addressdata = {
        "firstname":major[9], 
        "lastname":major[12],
        "street":["aaa_adm"],
        "city":easy5User.email_user,
        "country_id": "DE", # FR,BE,NL,DE,AT,
        "postcode":"aaa_adm",
        "telephone":"aaa_adm",
        "fax":easy5User.vt1,
        "is_default_billing": False,
        "is_default_shipping": False           
            }
    try:
        #c.service.customerInfo(sid,pos)
        resp = c.service.customerAddressCreate(sid,pos,addressdata)
        print "DONE: customer id=>",pos, major[0], "adm info 'address'=>", resp
        objekt = pos,":" ,major[0],resp
    except Exception,e:
        print pos,major[0],e
        objekt = pos,":" ,major[0],e
    pass
    container = []
    container.append(objekt)
    pickle.dump(container,open("log.pkl","a+"))


def updateUsersByAMDsIDs():
#===============================================================================
# updates users with additional address, which contains refering adm. 
# -> ad hoc solution for user - adm relation.                        
#===============================================================================
    #return a list from magento
    print "loading list...",time.now()
    try:
        import csv
        path = "C:/Users/Dawe/Downloads/customer_20130410_112304.csv"
        mageUsers = []
        with open(path , 'r') as f:
            reader = csv.reader(f)
            for row in reader:
                mageUsers.append(row)
    except Exception,e:
        print e
        mageUsers = c.service.customerCustomerList(sid)
    print "loaded",time.now() 
    #return a list of users from easy5
    easy5Users = easy5DB("stammdaten").read("SELECT stammdaten_oranier.user.email_user,stammdaten_oranier.user.vt1 FROM stammdaten_oranier.user")
    print len(mageUsers),len(easy5Users)
    for cnt,major in enumerate(mageUsers,1):
        if cnt < 17012:continue
        #[0] = email,[09] = firstname, [12] = lastname
        print cnt
        for x in easy5Users:
            #print x.email_user, major[0]
            x.email_user = unicode(x.email_user )
            major[0] = unicode(major[0])
            if x.email_user in major[0]:    
                print x.email_user,">-matches->",
                processUsersByAMDsIDs(cnt,major,x)
    

def assignRelatedToParents():
    AllProds=c.service.catalogProductList(sid)
    parents = [product for product in AllProds if product.type == "configurable"]
    children = [product for product in AllProds if product.type == "simple"]
    for cnt,parent in enumerate(parents,1):
        #The line bellow is for debugging And minimazing loops
        #if cnt < 321:continue
        print cnt,"/",len(parents)
        try:
            myChildren = [child.sku for child in children if parent.sku in child.sku]
        except Exception,e:
            child.sku,parent.sku,"\n",e
        accessories=[]
        for child in myChildren:
            rel = c.service.catalogProductLinkList(sid,"related",child,"sku")
            for one in rel:#restructure the dataobject
                accessories.append(one.sku)
        accessories = list(set(accessories))
        for a in accessories:
            try:
                c.service.catalogProductLinkAssign(sid,"related",parent.sku,a,None,"sku") #data || None
                print parent.sku,"connected to",a
            except Exception,e:
                print parent.sku,"failed to connect to",a,"\n",e
        pass
    pass
    
""" Reimport of all the products to magneto """
    

if False:#set to true only when loop_Thru_Tabs(create_Products) is executed  
    attributeSets = c.service.catalogProductAttributeSetList(sid)
#loopThruTabs(createProducts) # 1) 
#loopThruTabs(updateItemsCat) # 2) 


#loopThruTabs(expandAttributesOptions,["aaa_bestellnummern_kt","_bestnr"],["KT"])    # 3) 
#loopThruTabs(expandAttributesOptions,["aaa_bestellnummern_ht","_bestnr"],["HT"])    # 3) 
#expandAttributesOptions("HT","hauptmerkmale","aaa_merkmale_ht")                     # 3)
#expandAttributesOptions("KT","hauptmerkmale","aaa_merkmale_kt")                     # 3)
#expandAttributesOptions("KT","farbe","aaa_farben_kt")                               # 3)
#expandAttributesOptions("HT","farbe","aaa_farben_ht")                               # 3)
#expandAttributesOptions("HT","leistung","aaa_leistungsmerkmale_kt")                 # 3)

#TODO:oprav fci updateAdditionalAttrOfProduct pro farben,bestellnummern,leistungsmerkmale
# vypada to, ze jedine pro co to opravdu funguje je merkmale HT/KT a mozna bestelnummern KT

#loopThruTabs(updateAdditionalAttrOfProduct,["aaa_merkmale_ht","hauptmerkmal"],["HT"])        # 4)
#loopThruTabs(updateAdditionalAttrOfProduct,["aaa_merkmale_kt","merkmal"],["KT"])             # 4)
#loopThruTabs(updateAdditionalAttrOfProduct,["aaa_farben_ht","farbe"],["HT"])                 # 4)
#loopThruTabs(updateAdditionalAttrOfProduct,["aaa_farben_kt","farbe"],["KT"])                 # 4)
#loopThruTabs(updateAdditionalAttrOfProduct,["aaa_leistungsmerkmale_kt","leistung"],["KT"])   # 4)

#? tak jsou bestnr nastaveny nebo ne?
#loopThruTabs(updateAdditionalAttrOfProduct,["aaa_bestellnummern_kt","bestnr"],["KT"])        # 4)
#loopThruTabs(updateAdditionalAttrOfProduct,["aaa_bestellnummern_ht","bestnr"],["HT"])        # 4)


#createParentProd() # 5)

#updateParentsWithChildrenAttribs() # 6)        

#loopThruTabs(updateProductsPics,[c.service.catalogProductList(sid)]) # 7)

#loopThruTabs(linkProductsWithAccessories) # 8)

#updatePrices() # 9)

#assignRelatedToParents() # 10)

#checkParentsNamesAndFillIfNecesary() # 11)

"""grouping products together"""
#loopThruTabsExpandAttributeOptions()
#prirad aaa_bestellnummern_xx option ke spravenmu sku (tj jmeno produktu a option se musi shodovat), pote prirad atribut decek rodicum
#setBestellnummernToChildren() #done!
"""grouping products together"""
"""=============realated products========"""
#TODO: still in development! Important f() for final check
#loopThruTabs(checkMiscSkus)
#TODO:zkontroluj unikatnost aaa_*_ht/kt atributu!
#TODO:Attributes (merkmale,leistung,farben) asigned to the parent products. Both HT and KT.

"""" check calls """
#===============================================================================
# USERS/CUSTOMERS/DEALERS calls
# #uploadDealersAndAddresses() creates addresses for all 18000 users. Takes few days to finish
# #customerAddressUpdate()
# #importADMs()
# #updateUsersByAMDsIDs()
#===============================================================================

print "fertig!",time.now()
#TODO:cleanParentsPictures() shoud correct the pictures name. Not so importatnt
#TODO:discusse with Martin what to do with this table >>SELECT * FROM oraniekt.kochfelder_kombi;<<    
