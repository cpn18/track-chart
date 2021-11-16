def swap(obj1, obj2):
    """
      Swap two objects
    """
    return (obj2, obj1)

def survey_to_ft(survey):
    """
    Convert survey string to feet
    """
    whole, feet = survey.split('+')
    return int(whole)*100 + float(feet)

def ft_to_survey(feet):
    """
    Convert feet to survey string
    """
    whole = int(feet / 100)
    feet = float(feet - whole*100)
    return "%d+%.1f" % (whole, feet)
    
