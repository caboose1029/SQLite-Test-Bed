import sqlite3
import dataspoof as ds
import time

class IMU_DB:
    def __init__(self, db_name):
        self.conn = sqlite3.connect(db_name)
        self.cursor = self.conn.cursor()
        self.path = db_name

    def create_table(self):
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS imu_data (
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP PRIMARY KEY,
                acc_x REAL, acc_y REAL, acc_z REAL,
                mag_x REAL, mag_y REAL, mag_z REAL, 
                gyro_x REAL, gyro_y REAL, gyro_z REAL
            )
        ''')
        self.conn.commit()

    def insert_data(self, timestamp, acc_x, acc_y, acc_z, gyro_x, gyro_y, gyro_z, mag_x, mag_y, mag_z):
        self.cursor.execute("INSERT INTO imu_data VALUES (?, ?, ?, ?, ?, ?, ?)", (timestamp, acc_x, acc_y, acc_z, gyro_x, gyro_y, gyro_z, mag_x, mag_y, mag_z))
        self.conn.commit()

    def get_all_data(self):
        self.cursor.execute("SELECT * FROM imu_data")
        return self.cursor.fetchall()
    
    def get_data(self, start, end):
        self.cursor.execute("SELECT * FROM imu_data WHERE timestamp >= ? AND timestamp <= ?", (start, end))
        return self.cursor.fetchall()
    
    def get_current_data(self):
        self.cursor.execute("SELECT * FROM imu_data ORDER BY timestamp DESC LIMIT 1")
        return self.cursor.fetchall()
    
        
    def open_connection(self):
        self.conn = sqlite3.connect(self.path)
        self.cursor = self.conn.cursor()

    def close(self):
        self.conn.close()

data = ds.DataSpoofing(9)


if __name__ == "__main__":
    
    db = IMU_DB("imu_data.db")
    db.create_table()

    while True:
        try:
            acc_x, acc_y, acc_z, gyro_x, gyro_y, gyro_z, mag_x, mag_y, mag_z = data.generate_data()
            db.open_connection()
            db.insert_data(time.time(), acc_x, acc_y, acc_z, gyro_x, gyro_y, gyro_z, mag_x, mag_y, mag_z)
            print(db.get_current_data())
            db.close()

        except KeyboardInterrupt:
            break