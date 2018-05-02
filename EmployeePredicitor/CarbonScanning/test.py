def Is_palindrome(n):
    n.strip()
    n_new = ''.join(e for e in n if e.isalnum())
    def str_rever(n_new):      
        if len(n_new)<=1:
            return n_new
        else:        
            return n_new[-1] + str_rever( n_new[:-1] )
    n_rever = str_rever(n_new)
    if n_new.lower() == n_rever.lower():
        return True
    else:
        return False

if __name__ == "__main__" :
    n = "Wassamassaw – a town in South Dakota"
    print(Is_palindrome(n))
 