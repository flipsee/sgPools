from peewee import *

database = SqliteDatabase('sgPoolsData.db')

class UnknownField(object):
    pass

class BaseModel(Model):
    class Meta:
        database = database
        
class TotoResult(BaseModel):
    DrawNumber = CharField(db_column='drawNumber', null=False, unique=True, primary_key=True)
    DrawDate = DateField(db_column='drawDate', null=True)
    Win1 = IntegerField(db_column='win1', null=True)
    Win2 = IntegerField(db_column='win2', null=True)
    Win3 = IntegerField(db_column='win3', null=True)
    Win4 = IntegerField(db_column='win4', null=True)
    Win5 = IntegerField(db_column='win5', null=True)
    Win6 = IntegerField(db_column='win6', null=True)
    AdditionalNumber = IntegerField(db_column='additionalNumber', null=True)
    QueryString = CharField(db_column='queryString', null=False) 

    class Meta:
        db_table = 'TotoResult'

class FailedTotoResult(BaseModel):
    DrawNumber = CharField(db_column='drawNumber', null=False, unique=True, primary_key=True)
    
    class Meta:
        db_table = 'FailedTotoResult'

class ProcessedTotoResult(BaseModel):
    CombinationNumber = CharField(db_column='combinationNumber', null=False)
    DrawNumber = CharField(db_column='drawNumber', null=False)

    class Meta:
        primary_key = CompositeKey('CombinationNumber','DrawNumber')
        db_table = 'ProcessedTotoResult'


class sgPoolsBL(object):
    def __init__(self):
        database.connect()
        database.create_tables([TotoResult], safe=True)
        database.create_tables([FailedTotoResult], safe=True)
        database.create_tables([ProcessedTotoResult], safe=True)

    def atomic(self):
        return database.atomic()

    def close(self):
        database.close()
        
    ##### FailedTotoResult Table - Start #####
    def get_failedtotoresult(self):
        return FailedTotoResult.select()
        
    def delete_failedtotoresult(self, DrawNumber):
        q = FailedTotoResult.delete().where(FailedTotoResult.DrawNumber == DrawNumber)
        q.execute()

    def add_Failedtotoresult(self, DrawNumber):
        try:
            FailedTotoResult.create(DrawNumber=DrawNumber)
        except IntegrityError:
            raise ValueError("Data already exists.")
    ##### FailedTotoResult Table - End #####

    ##### TotoResult Table - Start #####
    def get_totoresults(self):
        return TotoResult.select()

    def get_totoresult(self, DrawNumber):
        try:
            return TotoResult.get(TotoResult.DrawNumber == DrawNumber)
        except:
            return None

    def delete_totoresult(self, DrawNumber):
        q = TotoResult.delete().where(TotoResult.DrawNumber == DrawNumber)
        q.execute()
    
    def clear_totoresults(self):
        q = TotoResult.delete()
        q.execute()

    def add_totoresults(self, rows):
        TotoResult.insert_many(rows).execute()        

    def add_dicttotoresult(self, Obj):
        self.add_totoresult(DrawNumber=Obj["DrawNumber"], DrawDate=Obj["DrawDate"], Win1=Obj["Win1"], Win2=Obj["Win2"], Win3=Obj["Win3"], Win4=Obj["Win4"], Win5=Obj["Win5"], Win6=Obj["Win6"], AdditionalNumber=Obj["AdditionalNumber"], QueryString=Obj["QueryString"])

    def add_totoresult(self, DrawNumber, DrawDate, Win1, Win2, Win3, Win4, Win5, Win6, AdditionalNumber, QueryString):
        try:
            TotoResult.create(DrawNumber=DrawNumber, DrawDate=DrawDate, Win1=Win1, Win2=Win2, Win3=Win3, Win4=Win4, Win5=Win5, Win6=Win6, AdditionalNumber=AdditionalNumber, QueryString=QueryString)
        except IntegrityError:
            raise ValueError("Data already exists.")

    def update_totodrawdate(self, DrawNumber, DrawDate):
        print("DB-DrawNumber: " + str(DrawNumber) + " DrawDate: " + str(DrawDate))
        q = TotoResult.update(DrawDate=DrawDate).where(TotoResult.DrawNumber == DrawNumber)
        q.execute() 

    ##### TotoResult Table - Stop #####

    ##### ProcessedTotoResult Table - Start #####
    def get_processedtotoresult(self):
        return ProcessedTotoResult.select()

    def delete_processedtotoresult(self, DrawNumber):
        q = ProcessedTotoResult.delete().where(ProcessedTotoResult.DrawNumber == DrawNumber)
        q.execute()

    def clear_processedtotoresults(self):
        q = ProcessedTotoResult.delete()
        q.execute()

    def add_processedtotoresult(self, CombinationNumber, DrawNumber):
        try:
            ProcessedTotoResult.create(CombinationNumber=CombinationNumber, DrawNumber=DrawNumber)
        except IntegrityError:
            raise ValueError("Data already exists.")

    def add_processedtotoresults(self, rows):
        ProcessedTotoResult.insert_many(rows).execute()

    def get_groupedtotoresult(self):
        return ProcessedTotoResult.select(ProcessedTotoResult.CombinationNumber, fn.GROUP_CONCAT(ProcessedTotoResult.DrawNumber).alias("DrawNumber")).group_by(ProcessedTotoResult.CombinationNumber).order_by(ProcessedTotoResult.CombinationNumber)
    ##### ProcessedTotoResult Table - End #####

