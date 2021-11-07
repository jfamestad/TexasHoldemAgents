from action import Action

def test_init_error():
    did_error = False
    try:
        action = Action("BET")
    except:
        did_error = True
    finally:
        assert did_error == True

def test_init_check():
    did_error = False
    try:
        action = Action("CHECK")
    except:
        did_error = True
    finally:
        assert did_error == False

def test_init_raise():
    did_error = False
    try:
        action = Action("RAISE")
    except:
        did_error = True
    finally:
        assert did_error == False

def test_init_call():
    did_error = False
    try:
        action = Action("CALL")
    except:
        did_error = True
    finally:
        assert did_error == False

def test_init_fold():
    did_error = False
    try:
        action = Action("FOLD")
    except:
        did_error = True
    finally:
        assert did_error == False

