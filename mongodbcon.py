__author__ = '최재혁'

import  pymongo

class  MongoDB():
    def __init__(self, collname):
        self.client = pymongo.MongoClient('localhost', 27017)
        self.db = self.client.get_database("xadb")
        self.collname = self.db.get_collection(collname)
    def getDB(self):
        return self.db
    def getDocumentCount(self, dictcondi):
        return self.collname.count(dictcondi)
    def insertManyDocuments(self, listdoc):
        self.collname.insert_many(listdoc)
    def insertOneDocument(self, doc):
        self.collname.insert_one(doc)
    def deleteManyDocuments(self, dictcondi):
        self.collname.delete_many(dictcondi)
    def findOneDocument(self, dictcondi):
        return self.collname.find_one(dictcondi)
    def findDocuments(self, dictcondi):
        listdoc = []
        for doc in self.collname.find(dictcondi) :
            listdoc.append(doc)
        return listdoc


