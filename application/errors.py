class GeneralError(Exception): pass
class ProcessingError(GeneralError): pass
class DatabaseError(GeneralError): pass
class UploadError(GeneralError): pass
class FatalError(Exception): pass
class StartupError(FatalError): pass
class CredentialsNotFound(FatalError): pass