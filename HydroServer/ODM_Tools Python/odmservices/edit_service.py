from odmdata import SessionFactory
from odmdata import Site
from odmdata import Variable
from odmdata import Unit
from odmdata import Series
from odmdata import DataValue
from odmdata import QualityControlLevel
from odmdata import Qualifier

from series_service import SeriesService

import sqlite3

class EditService():
    # Mutual exclusion: cursor, or connection_string
    def __init__(self, series_id, connection=None, connection_string="",  debug=False):
        # print "Series id: ", series_id
        self._connection = connection
        self._series_id = series_id
        self._filter_from_selection = False
        self._debug = debug

        if (connection_string is not ""):
            self._session_factory = SessionFactory(connection_string, debug)
            self._series_service = SeriesService(connection_string, debug)
        elif (factory is not None):
            self._session_factory = factory
            service_manager = ServiceManager()
            self._series_service = service_manager.get_series_service()
        else:
            # One or the other must be set
            print "Must have either a connection string or session factory"
            # TODO throw an exception
        
        self._edit_session = self._session_factory.get_session()

        if self._connection == None:
            series_service = SeriesService(connection_string, False)
            DataValues = series_service.get_data_values_by_series_id(series_id)
            self._connection = sqlite3.connect(":memory:", detect_types= sqlite3.PARSE_DECLTYPES)
            tmpCursor = self._connection.cursor()
            self.init_table(tmpCursor)
            tmpCursor.executemany("INSERT INTO DataValuesEdit VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)", DataValues)

        self._connection.commit()
        self._cursor = self._connection.cursor()

        self._populate_series()

    def _populate_series(self):
        # [(ID, value, datetime), ...]
        self._cursor.execute("SELECT ValueID, DataValue, LocalDateTime FROM DataValuesEdit ORDER BY LocalDateTime")
        results = self._cursor.fetchall()

        self._series_points = results
        self.reset_filter()

    def _test_filter_previous(self):
        if not self._filter_from_selection:
            self.reset_filter()

    ###################
    # Filters
    ###################
    # operator is a character, either '<' or '>'
    def filter_value(self, value, operator):
        self._test_filter_previous()

        if operator == '<': # less than
            for i in range(len(self._series_points)):
                # If it's not already in the selection, skip it
                if (self._filter_from_selection and not self._filter_list[i]):
                    continue
                if self._series_points[i][1] < value:
                    self._filter_list[i] = True
                else:
                    self._filter_list[i] = False
        if operator == '>': # greater than
            for i in range(len(self._series_points)):
                if (self._filter_from_selection and not self._filter_list[i]):
                    continue
                if self._series_points[i][1] > value:
                    self._filter_list[i] = True
                else:
                    self._filter_list[i] = False

    def filter_date(self, before, after):
        self._test_filter_previous()

        previous_date_filter = False
        if before != None:
            tmp = []
            for i in range(len(self._series_points)):
                if (self._filter_from_selection and not self._filter_list[i]):
                    continue
                if self._series_points[i][2] < before:
                    self._filter_list[i] = True
                else:
                    self._filter_list[i] = False
            previous_date_filter = True        # We've done a previous date filter
        if after != None:
            for i in range(len(self._series_points)):
                if ((previous_date_filter or self._filter_from_selection)
                     and not self._filter_list[i]):
                    continue
                if self._series_points[i][2] > after:
                    self._filter_list[i] = True
                else:
                    self._filter_list[i] = False

    # Data Gaps
    def data_gaps(self, value, time_period):
        length = len(self._series_points)

        value_sec = 0

        if time_period == 'second':
            value_sec = value
        if time_period == 'minute':
            value_sec = value * 60
        if time_period == 'hour':
            value_sec = value * 60 * 60
        if time_period == 'day':
            value_sec = value * 60 * 60 * 24

        tmp = {}

        for i in xrange(length):
            if (self._filter_from_selection and 
                not self._filter_list[i]):
                continue

            if i + 1 < length:      # make sure we stay in bounds
                point1 = self._series_points[i]
                point2 = self._series_points[i+1]
                interval = point2[2] - point1[2]
                interval_total_sec = interval.total_seconds()

                if interval_total_sec >= value_sec:
                    tmp[i] = True
                    tmp[i+1] = True
        
        self.reset_filter()
        for key in tmp.keys():
            self._filter_list[key] = True

    def value_change_threshold(self, value):

        length = len(self._series_points)
        tmp = {}
        for i in xrange(length):
            if (self._filter_from_selection and 
                not self._filter_list[i]):
                continue

            if i + 1 < length:         # make sure we stay in bounds
                point1 = self._series_points[i]
                point2 = self._series_points[i+1]
                if abs(point1[1] - point2[1]) >= value:
                    tmp[i] = True
                    tmp[i + 1] = True

        self.reset_filter()
        for key in tmp.keys():
            self._filter_list[key] = True

    def select_points_tf(self, tf_list):
        self._filter_list = tf_list

    def select_points(self, id_list=[], datetime_list=[]):
        self.reset_filter()

        # This should be either one or the other. If it's both, id is used first.
        # If neither are set this function does nothing.
        if id_list != None:
            for i in range(len(self._series_points)):
                if self._series_points[i][0] in id_list:
                    self._filter_list[i] = True
        elif datetime_list != None:
            for i in range(len(self._series_points)):
                if self._series_points[i][2] in datetime_list:
                    self._filter_list[i] = True
        else:
            pass


    def reset_filter(self):
        self._filter_list = [False] * len(self._series_points)

    def toggle_filter_previous(self):
        self._filter_from_selection = not self._filter_from_selection


    ###################
    # Gets
    ###################
    def get_series(self):
        return self._series_service.get_series_by_id(self._series_id)

    def get_series_points(self):
        return self._series_points

    def get_filtered_points(self):
        tmp = []
        for i in range(len(self._series_points)):
            if self._filter_list[i]:
                tmp.append(self._series_points[i])

        return tmp

    def get_filter_list(self):
        return self._filter_list

    
    #################
    # Edits
    #################

    def change_value(self, value, operator):
        filtered_points = self.get_filtered_points()
        tmp_filtered_list = self._filter_list
        execute_string = "UPDATE DataValuesEdit SET DataValue = "
        if operator == '+':
            execute_string += " DataValue + %s " % (value)

        if operator == '-':
            execute_string += " DataValue - %s " % (value)

        if operator == '*':
            execute_string += " DataValue * %s " % (value)

        if operator == '=':
            execute_string += "%s " % (value)

        execute_string += "WHERE ValueID IN ("
        for i in range(len(filtered_points) - 1):
            execute_string += "%s," % (filtered_points[i][0])
        execute_string += "%s)" % (filtered_points[-1][0])
        self._cursor.execute(execute_string)

        self._populate_series()
        self._filter_list = tmp_filtered_list

    def add_points(self, points):
        query = "INSERT INTO DataValuesEdit (DataValue, ValueAccuracy, LocalDateTime, UTCOffset, DateTimeUTC, OffsetValue, OffsetTypeID, "
        query += "CensorCode, QualifierID, SampleID, SiteID, VariableID, MethodID, SourceID, QualityControlLevelID) "
        query += "VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)"
        self._cursor.executemany(query, points)
        self._populate_series()

    def delete_points(self):
        execute_string = "DELETE FROM DataValuesEdit WHERE ValueID IN ("
        filtered_points = self.get_filtered_points()
        num_filtered_points = len(filtered_points)
        if num_filtered_points > 0:
            for i in range(num_filtered_points-1):        # loop through the second-to-last active point
                execute_string += "%s," % (filtered_points[i][0])   # append its ID
            execute_string += "%s)" % (filtered_points[-1][0])  # append the final point's ID and close the set

            # Delete the points from the cursor
            self._cursor.execute(execute_string)

            self._populate_series()
    
    def interpolate(self):
        pass

    def flag(self, qualifier_id):
        filtered_points = self.get_filtered_points()
        query = "UPDATE DavaValuesEdit SET QualifierID = %s WHERE ValueID = ?" % (qualifier_id)
        self._cursor.executemany(query, [x[0] for x in filtered_points])

    ###################
    # Save/Restore
    ###################

    def restore(self):
        self._connection.rollback()
        self._populate_series()

    def save(self):
        # Save to sqlite memory DB, not real DB
        self._connection.commit()

    def write_to_db(self):
        # Save to real DB
        pass

    def reconcile_dates(self, parent_series_id):
        # append new data to this series
        pass

    def init_table(self, cursor):
        cursor.execute("""CREATE TABLE DataValuesEdit
                (ValueID INTEGER NOT NULL,
                DataValue FLOAT NOT NULL,
                ValueAccuracy FLOAT,
                LocalDateTime TIMESTAMP NOT NULL,
                UTCOffset FLOAT NOT NULL,
                DateTimeUTC TIMESTAMP NOT NULL,
                SiteID INTEGER NOT NULL,
                VariableID INTEGER NOT NULL,
                OffsetValue FLOAT,
                OffsetTypeID INTEGER,
                CensorCode VARCHAR(50) NOT NULL,
                QualifierID INTEGER,
                MethodID INTEGER NOT NULL,
                SourceID INTEGER NOT NULL,
                SampleID INTEGER,
                DerivedFromID INTEGER,
                QualityControlLevelID INTEGER NOT NULL,

                PRIMARY KEY (ValueID),
                UNIQUE (DataValue, LocalDateTime, SiteID, VariableID, MethodID, SourceID, QualityControlLevelID))
               """)