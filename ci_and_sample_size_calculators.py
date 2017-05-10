def multinomial_sample_size(width=0.05, miss=0.05):
  """This function calculates sample sizes for multiple option questions,
  based on a given miss-rate (alpha level), and the width of the desired confidence intervals.
  Only miss-rates of 0.05, 0.01, 0.005 and 0.001 are supported. For further information about this
  method see Thompson, The American Statestician (1987)"""
  
  ## Generate an object for the dn2-values indexed by the various alpha levels
  d2n = {'0.05' : 1.27359, '0.01': 1.96986, '0.005':2.28514, '0.001':3.02892}
  
  
  ## If Miss (alpha) is not a key to the dictionary above raise an error 
  if (str(miss) not in ['0.05', '0.01', '0.005', '0.001']):
    print "Miss can only be set to 0.05 0.01, please try again"
  
  ## Otherwise calculate the sample size
  else:
    sample_size=d2n[str(miss)]/(width**2)
    return round(sample_size + 0.4999999999) # The constant at the end ensures that the function rounds to the next
    # integer without importing a ceiling function from math or numpy

def multinomial_CI(N=100, miss=0.05):
  """This function calculates confidence intervals for multiple option questions, based on a given
  miss-rate (alpha level), and the sample size (N). Only miss-rates of 0.05, 0.01, 0.005 and 0.001
  are supported. For further information about this method Thompson, The American Statestician (1987)"""
  
  ## Generate an object for the dn2-values indexed by the various alpha levels
  d2n = {'0.05' : 1.27359, '0.01': 1.96986, '0.005':2.28514, '0.001':3.02892}
  
  ## If Miss (alpha) is not a key to the dictionary above raise an error 
  if (str(miss) not in ['0.05', '0.01', '0.005', '0.001']):
    print "Miss can only be set to 0.05 0.01, please try again"
  
  ## Otherwise calculate the width of the confidence intervals
  else:
    d=(d2n[str(miss)]/N)**0.5
    return round(d, 2)

