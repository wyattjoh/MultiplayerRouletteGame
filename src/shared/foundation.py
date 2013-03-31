import json

class CoreData:
    ident = []
    fields = []
    private = []
    """
    Class CoreData

    Provides fountation for data management of classes.

    NOTE: ALL CHILDREN MUST IMPLEMENT THE FOLLOWING CLASS
    VARIABLES (ident, fields, private). These are fields that contain
    the nessesary field names for identifying the class obj
    as well as the extra field objects in fields. Any fields listed in
    'private' will be got and set, but not serialized.
    """
    def get(self, key):
        """
        Gets a value from the self object
        """
        try:
            return getattr(self, key)
        except AttributeError:
            return None

    def clear(self):
        """
        Sets the values of all self attributes to None given a predesignated
        allowed fields list.
        """

        for f in self.fields + self.ident + self.private:
            setattr(self, f, None)

    def load(self, data):
        """
        Dispatches the correct loading method for the input
        data type.
        """

        if type(data) is str:
            self.unserialize_load(data)
        elif type(data) is dict:
            self._load(data)
        else:
            RuntimeError("Incorrect data type supplied to load.")

    def _load(self, data):
        """
        Loads the contents of a dictionary into self attributes given a
        predesignated allowed fields list.
        """
    
        for f in self.fields + self.ident + self.private:
            if f in data:
                setattr(self, f, data[f])
            else:
                setattr(self, f, None)

    def _update(self, update_data):
        """
        Updates the self variables that have listed names in the fields
        list with content of update_data, any fields not updated or not
        listed inside fields will not be changed
        """
        for key in update_data:
            if key in self.fields + self.ident + self.private:
                setattr(self, key, update_data[key])
                print("Dict update for {0} recieved and set to: {1}.".format(key, update_data[key]))

    def update(self, update_data):

        if type(update_data) is str:
            self.unserialize_update(update_data)
        elif type(update_data) is dict:
            self._update(update_data)
        else:
            RuntimeError("Incorrect data type supplied to update.")

    def _serialize(self, fields):
        """
        Generates a JSON string from the fields within fields. Any None
        value will not be included in the serialization.
        """

        output = {}

        for field in fields:
            value = getattr(self, field)
            if value is not None:
                output[field] = value

        return json.dumps(output)

    def serialize(self):
        return self._serialize(self.fields + self.ident)

    def dict_serialize(self):
        output = {}

        for field in self.ident:
            value = getattr(self, field)
            if value is not None:
                output[field] = value

        return output

    def _unserialize(self, json_data):
        """
        Reads from a JSON string and parses allowed field types. Output is
        a dictionary containing the parsed json data. To be used with
        unserialize_load and unserialize_update.
        """
        data = json.loads(json_data)

        data_parsed = {}

        for data_field in data:
            if data_field in self.fields + self.ident:
                data_parsed[data_field] = data[data_field]

        return data_parsed

    def unserialize_load(self, json_data):
        """
        Loads instance data from a json_data string into self, any fields
        not declared inside the json_data string will be set to None.
        """

        data = self._unserialize(json_data)

        for field in self.fields + self.ident:
            if field in data:
                setattr(self, field, data[field])
            else:
                setattr(self, field, None)

    def unserialize_update(self, json_data):
        """
        Loads instance data from a json_data string into self, any fields
        not declared inside the json_data string will not be changed.
        """

        data = self._unserialize(json_data)

        for field in self.fields + self.ident:
            if field in data:
                setattr(self, field, data[field])
