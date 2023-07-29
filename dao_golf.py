import cx_Oracle
import os


class GlfprUseDao:
    
    def __init__(self):
        
        self.connect = cx_Oracle.connect("team1_202212F", "java", "112.220.114.130:1521/xe")
        self.cursor = self.connect.cursor()
    
    def select(self, rcordNo):
         
        sql = f"""
            SELECT
               FILE_PATH
            FROM
            GLFPR_USE_RCORD WHERE RCORD_NO = '{rcordNo}'
        """
        
        self.cursor.execute(sql)

        result = self.cursor.fetchall()
        
        
        return result[0][0]
    
    def update(self, rcordNo, filePath):
        
        sql = f"""
            UPDATE GLFPR_USE_RCORD
                SET
            FILE_PATH = '{filePath}'
            WHERE
            RCORD_NO ='{rcordNo}'
        
        """
        
        self.cursor.execute(sql)
        self.connect.commit()
        
        return self.cursor.rowcount
    
   
    
    def __del__(self):
        self.cursor.close()
        self.connect.close()


if __name__ == '__main__':
    dp = GlfprUseDao()
    cnt = dp.update(1, "test")
    print(cnt)
    
