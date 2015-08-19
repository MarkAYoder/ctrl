import sys
sys.path.append('..')

import pytest

import numpy as np
import ctrl.block as block
import ctrl.block.linear as linear
import ctrl.system as system
import ctrl.system.tf as tf

def test1():

    num = np.array([1, 1])
    den = np.array([1, -1])
    sys = tf.DTTF(num, den)
    assert np.all(sys.num == num)
    assert np.all(sys.den == den)
    assert np.all(sys.state == np.zeros(2))

    num = np.array([1, 1])
    den = np.array([2, -1])
    sys = tf.DTTF(num, den)
    assert np.all(sys.num == num/2)
    assert np.all(sys.den == den/2)
    assert np.all(sys.state == np.zeros(2))

    num = np.array([1, 1, 3])
    den = np.array([1, -1])
    sys = tf.DTTF(num, den)
    assert np.all(sys.num == num)
    den = np.array([1, -1, 0])
    assert np.all(sys.den == den)
    assert np.all(sys.state == np.zeros(2))

    yk = sys.update(1)
    state = np.array([1, 0])
    assert np.all(sys.state == state)
    assert yk == 1

    yk = sys.update(-1)
    state = np.array([0, 1])
    assert np.all(sys.state == state)
    assert yk == 1

    yk = sys.update(2)
    state = np.array([2, 0])
    assert np.all(sys.state == state)
    assert yk == 5

    yk = sys.update(1)
    state = np.array([3, 2])
    assert np.all(sys.state == state)
    assert yk == 5

    sys.set_output(0)
    yk = sys.update(0)
    assert yk == 0

    sys.set_output(3)
    yk = sys.update(0)
    assert yk == 3
    
def test2():

    # PID = PI
    ierror = 0
    error = 0
    alg = tf.PID(3, 4, period = 6)
    err = 7 - 5
    ierror += 6. * (err + error) / 2
    assert alg.update(err) == 3 * err + 4 * ierror
    error = err

    err = -1 - 2
    ierror += 6. * (err + error) / 2
    assert alg.update(err) == 3 * err + 4 * ierror
    error = err

    # PID = PI + gain
    ierror = 0
    error = 0
    alg = tf.PID(3, 4, 0, period = 6)
    err = -2/100 * 7 - 5
    ierror += 6. * (err + error) / 2
    assert alg.update(err) == 3 * err + 4 * ierror
    error = err

    err = -2/100*(-1) - 2
    ierror += 6. * (err + error) / 2
    assert abs(alg.update(err) - (3 * err + 4 * ierror)) < 1e-6
    error = err

    # PID = PID
    ierror = 0
    error = 0
    alg = tf.PID(3, 4, .5, period = 6)
    err = 7 - 5
    ierror += 6. * (err + error) / 2
    assert alg.update(err) == 3 * err + 4 * ierror + .5 * (err - error) / 6
    error = err

    err = -1 - 2
    ierror += 6. * (err + error) / 2
    assert abs(alg.update(err) - (3 * err + 4 * ierror + .5 * (err - error) / 6)) < 1e-6
    error = err

    # PID = PID + gain
    ierror = 0
    error = 0
    alg = tf.PID(3, 4, .5, period = 6)
    err = -2/100 * 7 - 5
    ierror += 6. * (err + error) / 2
    assert (alg.update(err) - (3 * err + 4 * ierror + .5 * (err - error) / 6)) < 1e-6
    error = err

    err = -2/100*(-1) - 2
    ierror += 6. * (err + error) / 2
    assert (alg.update(err) - (3 * err + 4 * ierror + .5 * (err - error) / 4)) < 1e-6
    error = err

def test3():

    # G(z) = (z + 2)/(z - 1) = (1 + 2 q) / (1 - q)
    num1 = np.array([2, 1])
    den1 = np.array([-1, 1])
    sys = tf.zDTTF(num1, den1)
    num2 = np.array([1, 2])
    den2 = np.array([1, -1])
    assert np.all(sys.num == num2)
    assert np.all(sys.den == den2)

    # G(z) = (z + 2)/(z - 1) = (z - 1 + 3)/(z-1) = 1 + 3/(z-1)
    ss = sys.as_DTSS()
    A = np.array([1])
    B = np.array([1])
    C = np.array([3])
    D = np.array([1])
    assert np.all(A == ss.A)
    assert np.all(B == ss.B)
    assert np.all(C == ss.C)
    assert np.all(D == ss.D)

    y1 = sys.update(1)
    y2 = ss.update(1)
    assert y1 == y2
    #print(y1, y2)

    y1 = sys.update(-1)
    y2 = ss.update(-1)
    assert y1 == y2
    #print(y1, y2)

    y1 = sys.update(3)
    y2 = ss.update(3)
    assert y1 == y2
    #print(y1, y2)

    y1 = sys.update(0)
    y2 = ss.update(0)
    assert y1 == y2
    #print(y1, y2)

    # G(z) = z/(z - 1) = 1 / (1 - q)
    num1 = np.array([0, 1])
    den1 = np.array([-1, 1])
    sys = tf.zDTTF(num1, den1)
    num2 = np.array([1, 0])
    den2 = np.array([1, -1])
    assert np.all(sys.num == num2)
    assert np.all(sys.den == den2)

    # G(z) = z/(z - 1) = (z - 1 + 1)/(z-1) = 1 + 1/(z-1)
    ss = sys.as_DTSS()
    A = np.array([1])
    B = np.array([1])
    C = np.array([1])
    D = np.array([1])
    assert np.all(A == ss.A)
    assert np.all(B == ss.B)
    assert np.all(C == ss.C)
    assert np.all(D == ss.D)

    y1 = sys.update(1)
    y2 = ss.update(1)
    assert y1 == y2
    #print(y1, y2)

    y1 = sys.update(-1)
    y2 = ss.update(-1)
    assert y1 == y2
    #print(y1, y2)

    y1 = sys.update(3)
    y2 = ss.update(3)
    assert y1 == y2
    #print(y1, y2)

    y1 = sys.update(0)
    y2 = ss.update(0)
    assert y1 == y2
    #print(y1, y2)

    # G(z) = 2/(z - 1)
    num1 = np.array([2, 0])
    den1 = np.array([-1, 1])
    sys = tf.zDTTF(num1, den1)
    num2 = np.array([0, 2])
    den2 = np.array([1, -1])
    assert np.all(sys.num == num2)
    assert np.all(sys.den == den2)

    ss = sys.as_DTSS()
    A = np.array([1])
    B = np.array([1])
    C = np.array([2])
    D = np.array([0])
    assert np.all(A == ss.A)
    assert np.all(B == ss.B)
    assert np.all(C == ss.C)
    assert np.all(D == ss.D)
    #print(ss.A, ss.B, ss.C, ss.D)

    y1 = sys.update(1)
    y2 = ss.update(1)
    assert y1 == y2
    #print(y1, y2)

    y1 = sys.update(-1)
    y2 = ss.update(-1)
    assert y1 == y2
    #print(y1, y2)

    y1 = sys.update(3)
    y2 = ss.update(3)
    assert y1 == y2
    #print(y1, y2)

    y1 = sys.update(0)
    y2 = ss.update(0)
    assert y1 == y2
    #print(y1, y2)

    # G(z) = z^2/(z - 1) = 1 / (1 - q)
    num1 = np.array([1, 0, 0])
    den1 = np.array([-1, 1])
    with pytest.raises(system.SysException):
        sys = tf.zDTTF(num1, den1)

    # G(z) = (z + 3)/(z^2 + 2 z - 1) = (q + 3 q^2)/(1 + 2 q - q^2)
    num1 = np.array([3, 1, 0])
    den1 = np.array([-1, 2, 1])
    sys = tf.zDTTF(num1, den1)
    num2 = np.array([0, 1, 3])
    den2 = np.array([1, 2, -1])
    assert np.all(sys.num == num2)
    assert np.all(sys.den == den2)

    ss = sys.as_DTSS()
    A = np.array([[0,1],[1,-2]])
    B = np.array([[0],[1]])
    C = np.array([[3,1]])
    D = np.array([[0]])
    assert np.all(A == ss.A)
    assert np.all(B == ss.B)
    assert np.all(C == ss.C)
    assert np.all(D == ss.D)
    #print('A =\n{}\nB =\n{}\nC =\n{}\nD =\n{}'.format(ss.A, ss.B, ss.C, ss.D))

    # yk = -2 yk-1 + yk-2 + uk-1 + 3 uk-2
    # u1 = 1   =>  y1 = 0
    # u1 = 1   =>  y1 = [3 1] [0; 0] = 0
    #              x2 = [0 1; 1 -2] [0; 0] + [0; 1] 1 = [0; 1]

    y1 = sys.update(1)
    y2 = ss.update(1)
    #print(y1, y2)
    assert y1 == 0 
    assert np.all(ss.state == np.array([[0],[1]]))
    assert y1 == y2

    # u2 = -1  =>  y2 = -2 y1 + u1 = 1
    # u2 = -1  =>  y2 = [3 1] [0; 1] = 1
    #              x3 = [0 1; 1 -2] [0; 1] + [0; 1] -1 
    #                 = [1; -2] + [0; -1] = [1; -3]

    y1 = sys.update(-1)
    y2 = ss.update(-1)
    #print(y1, y2)
    assert y1 == 1 
    assert np.all(ss.state == np.array([[1],[-3]]))
    assert y1 == y2

    # u3 = 3   =>  y3 = -2 y2 + y1 + u2 + 3 u1 = -2 + 0 + -1 + 3 = 0
    # u3 = 3   =>  y3 = [3 1] [1; -3] = 0
    #              x4 = [0 1; 1 -2] [1; -3] + [0; 1] 3 
    #                 = [-3; 7] + [0; 3] = [-3; 10]

    y1 = sys.update(3)
    y2 = ss.update(3)
    #print(y1, y2)
    assert y1 == 0 
    assert np.all(ss.state == np.array([[-3],[10]]))
    assert y1 == y2

    # u4 = 0   =>  y4 = -2 y3 + y2 + u3 + 3 u2 = 0 + 1 + 3 - 3 = 1
    # u4 = 0   =>  y4 = [3 1] [-3; 10] = 1
    #              x5 = [0 1; 1 -2] [-3; 10] + [0; 1] 0 
    #                 = [10; -23]

    y1 = sys.update(0)
    y2 = ss.update(0)
    #print(y1, y2)
    assert y1 == 1
    assert np.all(ss.state == np.array([[10],[-23]]))
    assert y1 == y2

    # G(z) = z^2/(z^2 + 2 z - 1) = 1 + (1 - 2 z)/(z^2 + 2 z - 1)
    num1 = np.array([0, 0, 1])
    den1 = np.array([-1, 2, 1])
    sys = tf.zDTTF(num1, den1)
    num2 = np.array([1, 0, 0])
    den2 = np.array([1, 2, -1])
    assert np.all(sys.num == num2)
    assert np.all(sys.den == den2)

    ss = sys.as_DTSS()
    A = np.array([[0,1],[1, -2]])
    B = np.array([[0],[1]])
    C = np.array([[1,-2]])
    D = np.array([[1]])
    assert np.all(A == ss.A)
    assert np.all(B == ss.B)
    assert np.all(C == ss.C)
    assert np.all(D == ss.D)
    #print('A =\n{}\nB =\n{}\nC =\n{}\nD =\n{}'.format(ss.A, ss.B, ss.C, ss.D))

    # yk = -2 yk-1 + yk-2 + uk
    # u1 = 1   =>  y1 = 1
    # u1 = 1   =>  y1 = [1 -2] [0; 0] + [1] 1 = 1
    #              x2 = [0 1; 1 -2] [0; 0] + [0; 1] 1 = [0; 1]

    y1 = sys.update(1)
    y2 = ss.update(1)
    #print(y1, y2)
    assert y1 == 1 
    assert np.all(ss.state == np.array([[0],[1]]))
    assert y1 == y2

    # u2 = -1  =>  y2 = -2 y1 + u2 = -2 - 1 = -3
    # u2 = -1  =>  y2 = [1 -2] [0; 1] + [1] -1 = -2 -1 = -3
    #              x3 = [0 1; 1 -2] [0; 1] + [0; 1] -1 
    #                 = [1; -2] + [0; -1] = [1; -3]

    y1 = sys.update(-1)
    y2 = ss.update(-1)
    #print(y1, y2)
    assert y1 == -3 
    assert np.all(ss.state == np.array([[1],[-3]]))
    assert y1 == y2

    # u3 = 3   =>  y3 = -2 y2 + y1 + u3 = 6 + 1 + 3 = 10
    # u3 = 3   =>  y3 = [1 -2] [1; -3] + [1] 3 = 1 + 6 + 3 = 10
    #              x4 = [0 1; 1 -2] [1; -3] + [0; 1] 3 
    #                 = [-3; 7] + [0; 3] = [-3; 10]

    y1 = sys.update(3)
    y2 = ss.update(3)
    #print(y1, y2)
    assert y1 == 10 
    assert np.all(ss.state == np.array([[-3],[10]]))
    assert y1 == y2

    # u4 = 0   =>  y4 = -2 y3 + y2 + u4 = - 20 - 3 + 0 = -23
    # u4 = 0   =>  y4 = [1 -2] [-3; 10] + [1] 0 = -3 -20 = -23
    #              x5 = [0 1; 1 -2] [-3; 10] + [0; 1] 0 
    #                 = [10; -23]

    y1 = sys.update(0)
    y2 = ss.update(0)
    #print(y1, y2)
    assert y1 == -23
    assert np.all(ss.state == np.array([[10],[-23]]))
    assert y1 == y2

if __name__ == "__main__":

    test1()
    test2()
    test3()