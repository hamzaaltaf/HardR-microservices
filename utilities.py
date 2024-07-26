class Utilities():
    
    @classmethod
    def error_formatter(cls, errors):
        if hasattr(errors, 'to_dict'):
            errors = errors.to_dict()
            formatted_errors = []
            for field, message in errors.items():
                formatted_errors.append(f"{field} {message.lower()}")
            formatted_errors = ', '.join(formatted_errors)
            return formatted_errors
        else: 
            return str(errors)