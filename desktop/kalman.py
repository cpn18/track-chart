import sys
import json
import numpy as np
from numpy import pi, cos, sin, sqrt, diag
from numpy.linalg import inv
from numpy.random import randn

dt = 1.0

# position
x = []
y = []
with open(sys.argv[1], "r") as f:
    for line in f:
        if line[0] == "#":
            continue
        items = line.split()
        if items[1] == "TPV":
            obj = json.loads(" ".join(items[2:-1]))
        #elif items[1] == "SKY":
        #    obj = json.loads(" ".join(items[2:-1]))
        else:
            continue
        if 'lon' in obj and 'lat' in obj:
            x.append(obj['lon'])
            y.append(obj['lat'])

# velocity
dxdt = [0]
dydt = [0]
for i in range(1,len(x)):
    dxdt.append(x[i] - x[i-1])
    dydt.append(y[i] - y[i-1])

# accel
d2xdt2 = [0]
d2ydt2 = [0]
for i in range(1,len(x)):
    d2xdt2.append(dxdt[i] - dxdt[i-1])
    d2ydt2.append(dydt[i] - dydt[i-1])

# jerk
d3xdt3 = [0]
d3ydt3 = [0]
for i in range(1,len(x)):
    d3xdt3.append(d2xdt2[i] - d2xdt2[i-1])
    d3ydt3.append(d2ydt2[i] - d2ydt2[i-1])

x = np.array(x)
y = np.array(y)
dxdt = np.array(dxdt)
dydt = np.array(dydt)
d2xdt2 = np.array(d2xdt2)
d2ydt2 = np.array(d2ydt2)
d3xdt3 = np.array(d3xdt3)
d3ydt3 = np.array(d3ydt3)

# http://www.pyrunner.com/weblog/2018/04/12/kalman-example/

# angular speed (scalar)
omega = (dxdt*d2ydt2 - dydt*d2xdt2) / (dxdt**2 + dydt**2)

# speed (scalar)
speed = sqrt(dxdt**2 + dydt**2)

# measurement error
gps_sig = 0   #  0.1
omega_sig = 0 #  0.3
speed_sig = 0 #  0.1

# noisy measurements
x_gps = x + gps_sig * randn(*x.shape)
y_gps = y + gps_sig * randn(*y.shape)
omega_sens = omega + omega_sig * randn(*omega.shape)
speed_sens = speed + speed_sig * randn(*speed.shape)

A = np.array([
    [1, dt, (dt**2)/2, 0, 0, 0],
    [0, 1, dt, 0, 0, 0],
    [0, 0, 1, 0, 0, 0],
    [0, 0, 0, 1, dt, (dt**2)/2],
    [0, 0, 0, 0, 1, dt],
    [0, 0, 0, 0, 0, 1],
    ])

Q1 = np.array([(dt**3)/6, (dt**2)/2, dt, 0, 0, 0])
Q1 = np.expand_dims(Q1, 1)
Q2 = np.array([0, 0, 0, (dt**3)/6, (dt**2)/2, dt])
Q2 = np.expand_dims(Q2, 1)

j_var = max(np.var(d3xdt3), np.var(d3ydt3))
Q = j_var * (Q1 @ Q1.T + Q2 @ Q2.T)

H = np.array([
    [1, 0, 0, 0, 0, 0],
    [0, 0, 0, 1, 0, 0],
    ])


R = diag(np.array([gps_sig**2, gps_sig**2]))

x_init = np.array([x[0], dxdt[0], d2xdt2[0], y[0], dydt[0], d2ydt2[0]])
P_init = 0.01 * np.eye(len(x_init))  # small initial prediction error



# create an observation vector of noisy GPS signals
observations = np.array([x_gps, y_gps]).T

# matrix dimensions
nx = Q.shape[0]
ny = R.shape[0]
nt = observations.shape[0]

# allocate identity matrix for re-use
Inx = np.eye(nx)

# allocate result matrices
x_pred = np.zeros((nt, nx))      # prediction of state vector
P_pred = np.zeros((nt, nx, nx))  # prediction error covariance matrix
x_est = np.zeros((nt, nx))       # estimation of state vector
P_est = np.zeros((nt, nx, nx))   # estimation error covariance matrix
K = np.zeros((nt, nx, ny))       # Kalman Gain

# set initial prediction
x_pred[0] = x_init
P_pred[0] = P_init

# for each time-step...
for i in range(nt):

    # prediction stage
    if i > 0:
        x_pred[i] = A @ x_est[i-1]
        P_pred[i] = A @ P_est[i-1] @ A.T + Q

    # estimation stage
    y_obs = observations[i]
    K[i] = P_pred[i] @ H.T @ inv((H @ P_pred[i] @ H.T) + R)
    x_est[i] = x_pred[i] + K[i] @ (y_obs - H @ x_pred[i])
    P_est[i] = (Inx - K[i] @ H) @ P_pred[i]

for smooth in x_est:
    print(smooth[0], smooth[3])
