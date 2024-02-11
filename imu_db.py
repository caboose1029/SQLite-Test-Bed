import sqlite3
import dataspoof as ds
import time
import matplotlib.pyplot as plt

class Cubesat_DB:
    def __init__(self, db_name):
        self.conn = sqlite3.connect(db_name)
        self.cursor = self.conn.cursor()
        self.path = db_name

    def create_imu_table(self):
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS imu_data (
                run_id INTEGER,
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                delta_time REAL,
                acc_x REAL, acc_y REAL, acc_z REAL,
                mag_x REAL, mag_y REAL, mag_z REAL, 
                gyro_x REAL, gyro_y REAL, gyro_z REAL
            )
        ''')
        self.conn.commit()

    def create_odrive_table(self):
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS odrive_data (
                run_id INTEGER,
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                delta_time REAL,
                position REAL, velocity REAL, torque_target REAL,
                torque_estimate REAL, bus_voltage REAL, bus_current REAL, 
                iq_setpoint REAL, iq_measured REAL, electrical_power REAL, mechanical_power REAL
            )
        ''')
        self.conn.commit()

    def insert_imu_data(self, run_id, dt, acc_x, acc_y, acc_z, gyro_x, gyro_y, gyro_z, mag_x, mag_y, mag_z):
        self.cursor.execute('''
                            INSERT INTO imu_data (run_id, delta_time, acc_x, acc_y, acc_z, gyro_x, gyro_y, gyro_z, mag_x, mag_y, mag_z) 
                            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                            (run_id, dt, acc_x, acc_y, acc_z, gyro_x, gyro_y, gyro_z, mag_x, mag_y, mag_z))
        self.conn.commit()

    def insert_odrive_data(self, run_id, dt, position, velocity, torque_target, torque_estimate, bus_voltage, bus_current, iq_setpoint, iq_measured, electrical_power, mechanical_power):
        self.cursor.execute('''INSERT INTO odrive_data (run_id, delta_time, position, velocity, torque_target, torque_estimate, bus_voltage,
                               bus_current, iq_setpoint, iq_measured, electrical_power, mechanical_power) 
                            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                             (run_id, dt, position, velocity, torque_target, torque_estimate, bus_voltage,
                               bus_current, iq_setpoint, iq_measured, electrical_power, mechanical_power))
        self.conn.commit()

    def get_all_data(self):
        self.cursor.execute("SELECT * FROM imu_data")
        return self.cursor.fetchall()
    
    def get_data(self, start, end):
        self.cursor.execute("SELECT * FROM imu_data WHERE delta_time >= ? AND delta_time <= ?", (start, end))
        return self.cursor.fetchall()
    
    def get_current_data(self):
        self.conn = sqlite3.connect(self.path)
        self.cursor.execute("SELECT * FROM imu_data ORDER BY id DESC LIMIT 1")
        return self.cursor.fetchall()
    
    def query_run(self):
        run_imu = None
        run_odrive = None

        self.cursor.execute("SELECT run_id FROM imu_data ORDER BY run_id DESC LIMIT 1")
        run_imu = self.cursor.fetchone()
        self.cursor.execute("SELECT run_id FROM odrive_data ORDER BY run_id DESC LIMIT 1")
        run_odrive = self.cursor.fetchone()

        if run_imu and run_odrive:
            run_imu = run_imu[0]  # Extract the integer value from the tuple
            run_odrive = run_odrive[0]
            return max(run_imu, run_odrive)
        elif run_imu:
            return run_imu[0]
        elif run_odrive:
            return run_odrive[0]
        else:
            return 0

    def open_connection(self):
        self.conn = sqlite3.connect(self.path)
        self.cursor = self.conn.cursor()

    def close_connection(self):
        self.conn.close()

    def create_joined_table(self):
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS joined_data1 AS
            SELECT * FROM imu_data JOIN odrive_data ON imu_data.delta_time = odrive_data.delta_time
        ''')
        self.conn.commit()



if __name__ == "__main__":
    
    print("Starting...")
    data_imu = ds.DataSpoofing(9)
    data_odrive = ds.DataSpoofing(10)
    
    t0 = time.time()
    print(t0)

    db = Cubesat_DB("cubesat_data.db")
    db.open_connection()
    db.create_imu_table()
    db.create_odrive_table()
    run_id = db.query_run() + 1
    print(run_id)

    while True:
        try:
            dt = round(time.time() - t0, 2)
            acc_x, acc_y, acc_z, gyro_x, gyro_y, gyro_z, mag_x, mag_y, mag_z = data_imu.generate_data()
            position, velocity, torque_target, torque_estimate, bus_voltage, bus_current, iq_setpoint, iq_measured, electrical_power, mechanical_power = data_odrive.generate_data()


            db.open_connection()
            

            
            db.insert_imu_data(run_id, dt, acc_x, acc_y, acc_z, gyro_x, gyro_y, gyro_z, mag_x, mag_y, mag_z)
            db.insert_odrive_data(run_id, dt, acc_x, velocity, torque_target, torque_estimate, bus_voltage, bus_current, iq_setpoint, iq_measured, electrical_power, mechanical_power)
            
            print(db.get_current_data())

        except KeyboardInterrupt:
            db.create_joined_table()
            db.close_connection()
            break

