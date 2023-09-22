"""
Utilities
"""

def swap(obj1, obj2):
    """
      Swap two objects
    """
    return (obj2, obj1)

def survey_to_ft(survey):
    """
    Convert survey string to feet
    """
    try:
        whole, feet = survey.split('+')
    except ValueError as ex:
        print(survey)
        raise ex
    return int(whole)*100 + float(feet)

def ft_to_survey(feet):
    """
    Convert feet to survey string
    """
    whole = int(feet / 100)
    feet = float(feet - whole*100)
    return ("%d+%.1f" % (whole, feet)).replace(".0","")

if __name__ == "__main__":
    assert swap(1,2) == (2,1)
    assert survey_to_ft("1234+56") == 123456
    assert survey_to_ft("1234+56.7") == 123456.7
    assert ft_to_survey(123456) == "1234+56"
    assert ft_to_survey(123456.7) == "1234+56.7"
