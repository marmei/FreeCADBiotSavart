import sys, scipy, numpy, os
import scipy.weave as weave
from scipy.weave import converters
from scipy.constants import mu_0, pi

def BiotLineIntegral(vect_arr, r_p, current=1.0):
    """
    Calculates the magnetic flux density of from a list of points
    (vect_arr) that represent a discretization of a conductor.
    The magnetic flux density is calculated for r_p positions.
    
    Parameters
    ----------
    vect_arr: array([[x_0,y_0,z_0], ... , [x_n,y_n,z_n]])
    r_p: array([[x_0,y_0,z_0], ... , [x_n,y_n,z_n]])

    All coordinates are in mm

    Returns
    ----------
    Magnetric flux density Bfield, same as r_p
    
    """
    bfield = scipy.empty_like(r_p, scipy.float64)
    code = """
    #include <iostream>
    #include <math.h>
    #include <assert.h>
    for(int ir_p = 0; ir_p < size_r_p; ir_p++) {
        vec3 wire_pre = { vect_arr(0,0), vect_arr(0,1), vect_arr(0,2) };
        vec3 bfield_vec = { 0.0, 0.0, 0.0 };
        vec3 vec3r_p = { r_p(ir_p, 0), r_p(ir_p, 1), r_p(ir_p, 2) };  
        for(int i_v  = 1; i_v < size_vect_arr; i_v++) {
            vec3 vec3_arr = { vect_arr(i_v,0), vect_arr(i_v,1), vect_arr(i_v,2) };
            vec3 dl = vec3_diff( vec3_arr, wire_pre);
            vec3 rs = vec3_arr;
            vec3 r  = vec3_diff( vec3r_p, rs );
            double r_length = vec3_abs(r);
            bfield_vec      =  vec3_add( vec3_scale( vec3_cross( dl, r), 1.0 / pow( r_length, 3)), bfield_vec );
            wire_pre        = vec3_arr;
        }
        bfield(ir_p, 0) = bfield_vec.x ;
        bfield(ir_p, 1) = bfield_vec.y ;
        bfield(ir_p, 2) = bfield_vec.z ;
    }
    return_val = 1;
    """
    size_r_p          = r_p[:, 0].size
    size_vect_arr     = vect_arr[:, 0].size
    os.path.realpath(__file__)
    support_code = open( os.path.dirname(__file__) + "/biot_blitz_support.cpp" )
    scipy.weave.inline(code,
                       ["r_p", "size_r_p", "bfield", "vect_arr", "size_vect_arr"],
                       type_converters=converters.blitz,
                       support_code=support_code.read(),
                       compiler='gcc' )
    return bfield * mu_0 * 1000.0 * 1.0/(4.0 * pi)
        
if __name__ == '__main__':
    print "test"
