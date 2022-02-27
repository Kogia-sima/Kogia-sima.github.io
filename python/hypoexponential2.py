import numpy as np
import matplotlib.pyplot as plt
# from matplotlib import rcParams
from typing import Any

plt.style.use('ggplot')


def hypoexponential(x, lam1, lam2) -> Any:
    if lam1 == lam2:
        return lam1 * lam2 * x * np.exp(-lam1 * x)
    coef = lam1 * lam2 / (lam1 - lam2)
    return coef * (np.exp(-lam2 * x) - np.exp(-lam1 * x))


def main() -> None:
    x = np.linspace(0.0, 0.5, 500)

    params = [
        [10, 10],
        [20, 20],
        [30, 30]
    ]

    plt.figure(figsize = (8, 4), dpi = 120)

    for param in params:
        label = r'$\lambda_1 = {:.1f}, \lambda_2 = {:.1f}$'.format(
            param[0], param[1]
        )

        y = hypoexponential(x, param[0], param[1])
        plt.plot(x, y, label=label)

    plt.legend()
    plt.savefig('hypoexponential2.png')
    plt.show()


if __name__ == '__main__':
    main()
