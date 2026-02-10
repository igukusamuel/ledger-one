def post_to_gl(journals):
    gl = {}

    for j in journals:
        gl[j.account] = gl.get(j.account, 0) + j.debit - j.credit

    return gl
