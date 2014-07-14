from ags.base import Properties


class UploadItem(Properties):
    """Upload item properties"""

    def get_properties(self):
        props = super(UploadItem, self).get_properties()
        props.update({
            'id': "itemID",
            'name': "itemName",
            'description': "description",
            'path_on_server': "pathOnServer",
            'date': "date",
            'committed': "committed"
        })
        return props