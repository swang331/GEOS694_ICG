import time
import sys
import numpy as np
import matplotlib.pyplot as plt
from concurrent.futures import ProcessPoolExecutor, as_completed

STEP = 0.00025

def gaussian2D(x, y, sigma):
    return (1/(2*np.pi*sigma**2))*np.exp(-1*(x**2+y**2)/(2*sigma**2))

def plot(z):
    plt.imshow(z.T)
    plt.gca().invert_yaxis()  # flip axes to get imshow to plot representatively
    plt.xlabel("X"); plt.ylabel("Y"); plt.title(f"{z.shape} points")
    plt.gca().set_aspect(1)

def main(limit, sigma=1):
    xmin, xmax, ymin, ymax = limit
    X = np.arange(float(xmin), float(xmax), STEP)
    Y = np.arange(float(ymin), float(ymax), STEP)
    Z = []  # 1D array
    for x in X:
        for y in Y:
            Z.append(gaussian2D(x, y, sigma))
    # ZZ = np.array(Z).reshape(len(X), len(Y))  # 2D array
    # plot(ZZ)

    return np.array(Z)

if __name__ == "__main__":
    start = time.time()
    # main(float(sys.argv[1]), float(sys.argv[2]), float(sys.argv[3]), float(sys.argv[4]))

    max_workers = 16
    serial = False

    xmin = -2
    xmax = 2
    ymin = -2
    ymax = 2

    X = np.arange(float(xmin), float(xmax), STEP)
    Y = np.arange(float(ymin), float(ymax), STEP)
    
    limits = []
    x0 = xmin

    for x1 in np.linspace(xmin, xmax, max_workers + 1)[1:]:
        limits.append([int(x0), int(x1), ymin, ymax])
        x0 = x1

    z = np.array([])

    with ProcessPoolExecutor(max_workers=max_workers) as executor: 
        futures = {executor.submit(main, limit): i for i, limit in enumerate(limits)}
        results = {}
        for future in as_completed(futures):
            i = futures[future]
            results[i] = future.result()

        for i in sorted(results.keys()):  # Sort in order before stiching
            z = np.append(z, results[i])


    plot(z.reshape(len(X), len(Y)))

    elapsed = time.time() - start
    print(f"Elapsed Time: {elapsed}s")

    plt.show()