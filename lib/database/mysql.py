# import mysql.connector
#
# class Mysql:
#     def __init__(self,):
#
#     def __select_build(self):
#         source_sql = "select [Field] from [Table] [Join] [Where]"
#
#
#
#
# class ConfigManager:
#     def __init__(self,config):
#         self.config = config
#         self.connector = {}
#         for  i in self.config:
#             c = mysql.connector.connect(**i)
#             self.connector[i["id"]] = c
#     def get(self,id):
#         return self.connector[id]