# dotDict 
# dotdict class of dictionaries!
# https://stackoverflow.com/questions/2352181/how-to-use-a-dot-to-access-members-of-dictionary
# related: https://dev.to/bitecode/use-dot-syntax-to-access-dictionary-key-python-tips-10ec
# dict.a = "b"
# dict.a
# del dict.a
class dotDict(dict):
    """dot.notation access to dictionary attributes"""
    __getattr__ = dict.get
    __setattr__ = dict.__setitem__
    __delattr__ = dict.__delitem__