###############################################################################
#   RazorThinExponentialDiskPotential.py: class that implements the razor thin
#                                         exponential disk potential
#
#                                      rho(R,z) = rho_0 e^-R/h_R delta(z)
###############################################################################
import numpy as nu
from scipy import special, integrate
from Potential import Potential
_TOL= 1.4899999999999999e-15
_MAXITER= 20
class RazorThinExponentialDiskPotential(Potential):
    """Class that implements the razor-thin exponential disk potential
    rho(R,z) = rho_0 e^-R/h_R delta(z)"""
    def __init__(self,amp=1.,ro=1.,hr=1./3.,
                 maxiter=_MAXITER,tol=0.001,normalize=False,
                 new=True,glorder=100):
        """
        NAME:
           __init__
        PURPOSE:
           initialize a razor-thin-exponential disk potential
        INPUT:
           amp - amplitude to be applied to the potential (default: 1)
           hr - disk scale-length in terms of ro
           tol - relative accuracy of potential-evaluations
           maxiter - scipy.integrate keyword
           normalize - if True, normalize such that vc(1.,0.)=1., or, if 
                       given as a number, such that the force is this fraction 
                       of the force necessary to make vc(1.,0.)=1.
        OUTPUT:
           RazorThinExponentialDiskPotential object
        HISTORY:
           2012-12-27 - Written - Bovy (IAS)
        """
        Potential.__init__(self,amp=amp)
        self._new= new
        self._glorder= glorder
        self._ro= ro
        self._hr= hr
        self._alpha= 1./self._hr
        self._maxiter= maxiter
        self._tol= tol
        self._glx, self._glw= nu.polynomial.legendre.leggauss(self._glorder)
        if normalize:
            self.normalize(normalize)
        #Load Kepler potential for large R
        #self._kp= KeplerPotential(normalize=4.*nu.pi/self._alpha**2./self._beta)

    def _evaluate(self,R,z,phi=0.,t=0.,dR=0,dphi=0):
        """
        NAME:
           _evaluate
        PURPOSE:
           evaluate the potential at (R,z)
        INPUT:
           R - Cylindrical Galactocentric radius
           z - vertical height
           phi - azimuth
           t - time
        OUTPUT:
           potential at (R,z)
        HISTORY:
           2012-12-26 - Written - Bovy (IAS)
        """
        if dR == 1 and dphi == 0:
            return -self._Rforce(R,z,phi=phi,t=t)
        elif dR == 0 and dphi == 1:
            return -self._phiforce(R,z,phi=phi,t=t)
        elif dR == 2 and dphi == 0:
            return self._R2deriv(R,z,phi=phi,t=t)
        elif dR != 0 and dphi != 0:
            raise NotImplementedWarning("High-order derivatives for RazorThinExponentialDiskPotential not implemented")
        if self._new:
            #if R > 6.: return self._kp(R,z)
            if z == 0.:
                y= 0.5*self._alpha*R
                return -nu.pi*R*(special.i0(y)*special.k1(y)-special.i1(y)*special.k0(y))
            kalphamax= 10.
            ks= kalphamax*0.5*(self._glx+1.)
            weights= kalphamax*self._glw
            sqrtp= nu.sqrt(z**2.+(ks+R)**2.)
            sqrtm= nu.sqrt(z**2.+(ks-R)**2.)
            evalInt= nu.arcsin(2.*ks/(sqrtp+sqrtm))*ks*special.k0(self._alpha*ks)
            return -2.*self._alpha*nu.sum(weights*evalInt)
        raise NotImplementedError("Not new=True not implemented for RazorThinExponentialDiskPotential")

    def _Rforce(self,R,z,phi=0.,t=0.):
        """
        NAME:
           Rforce
        PURPOSE:
           evaluate radial force K_R  (R,z)
        INPUT:
           R - Cylindrical Galactocentric radius
           z - vertical height
           phi - azimuth
           t - time
        OUTPUT:
           K_R (R,z)
        HISTORY:
           2012-12-27 - Written - Bovy (IAS)
        """
        if self._new:
            #if R > 6.: return self._kp(R,z)
            if z == 0.:
                y= 0.5*self._alpha*R
                return -2.*nu.pi*y*(special.i0(y)*special.k0(y)-special.i1(y)*special.k1(y))
            kalphamax1= R
            ks1= kalphamax1*0.5*(self._glx+1.)
            weights1= kalphamax1*self._glw
            sqrtp= nu.sqrt(z**2.+(ks1+R)**2.)
            sqrtm= nu.sqrt(z**2.+(ks1-R)**2.)
            evalInt1= ks1**2.*special.k0(ks1*self._alpha)*((ks1+R)/sqrtp-(ks1-R)/sqrtm)/nu.sqrt(R**2.+z**2.-ks1**2.+sqrtp*sqrtm)/(sqrtp+sqrtm)
            if R < 10.:
                kalphamax2= 10.
                ks2= (kalphamax2-kalphamax1)*0.5*(self._glx+1.)+kalphamax1
                weights2= (kalphamax2-kalphamax1)*self._glw
                sqrtp= nu.sqrt(z**2.+(ks2+R)**2.)
                sqrtm= nu.sqrt(z**2.+(ks2-R)**2.)
                evalInt2= ks2**2.*special.k0(ks2*self._alpha)*((ks2+R)/sqrtp-(ks2-R)/sqrtm)/nu.sqrt(R**2.+z**2.-ks2**2.+sqrtp*sqrtm)/(sqrtp+sqrtm)
                return -2.*nu.sqrt(2.)*self._alpha*nu.sum(weights1*evalInt1
                                                          +weights2*evalInt2)
            else:
                return -2.*nu.sqrt(2.)*self._alpha*nu.sum(weights1*evalInt1)
        raise NotImplementedError("Not new=True not implemented for RazorThinExponentialDiskPotential")