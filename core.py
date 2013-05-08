import collections
class Objexe():
    def __init__( self, id, exe, var ):
        self.exe = exe
        self.var = var
        self.id = id

class Core():
    def __init__( self ):
        self.pile = collections.deque()
        self.pile_resultat = {}
        self.nid = 0

    def add_to_pile( self, exe, var=None ):
        self.nid += 1
        objexe = Objexe( self.nid, exe, var )
        self.pile.append( objexe )
        return self.nid

    def exec_next( self ):
        objexe = self.pile.popleft()
        if objexe.var == None:
            self.pile_resultat[objexe.id] = objexe.exe()
        else:
            self.pile_resultat[objexe.id] = objexe.exe( *objexe.var )

    def get_result( self, id ):
        result = self.pile_resultat[id]
        del self.pile_resultat[id]
        return result

