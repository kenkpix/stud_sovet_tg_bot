from pymongo import MongoClient, DESCENDING
# import certifi
import ssl


class Database:
    def __init__(self, db_name):
        self.client = MongoClient('mongodb+srv://stud_admin:detroit313@clustertg-bot.yga5e.mongodb.net'
                                  '/stud_sovet?retryWrites=true&w=majority',
                                  ssl=True, ssl_cert_reqs='CERT_NONE')
        self.db = self.client[db_name]
        # self.db = self.client.stud_sovet

    # def find_number(self, collection, col, number):
    #     return True if self.db[collection].count_documents({col: number}) != 0 else False

    def info_about_user(self, collection, number):
        info_row = self.db[collection].aggregate([
            {"$match": {"user_id": number}}
        ])
        for info in info_row:
            return info if info is not None else False

    # def make_prediction(self, collection, number):
    #     prediction = self.db[collection].aggregate([
    #         {"$match": {"telephone_number": {"$ne": number}}},
    #         {"$sample": {"size": 1}}
    #     ])

    #     for data in prediction:
    #         return data

    def update_db(self, collection, col, number_to_del):
        return self.db[collection].delete_one({
            col: number_to_del
        })

    def record_prediction(self, collection, data):
        return self.db[collection].insert(data)

    def get_last_order(self, collection):
        report = self.db[collection].find_one(
            sort=[('_id', DESCENDING)])
        return report
        # return self.db[collection].find().sort({"_id":-1}).limit(1)
        # return self.db[collection].sort('_id', DESCENDING).find_one()

    # temporary functions for debuging
    # def insert_all_data(self, collection, data):
    #     return self.db[collection].insert_many(data)

    # def create_collection(self, collection_name):
    #     return self.db.create_collection(collection_name)

    # def drop_collection(self, collection):
    #     return self.db[collection].drop()

# db = Database('stud_sovet')
# print(db.info_about_user('abit', 458))
