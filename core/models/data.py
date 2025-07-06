class Data:
    
    def __init__(self, url = '', environment = '', backup_location = '', file_template = '', options = '', threads = 0, extension = ''):
        self.url = url
        self.environment = environment
        self.backup_location = backup_location
        self.file_template = file_template
        self.options = options
        self.threads = threads
        self.extension = extension