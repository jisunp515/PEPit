from PEPit import PEP
from PEPit.operators import LipschitzOperator


def wc_optimal_contractive_halpern_iteration(n, gamma, verbose=1):
    """
    Consider the fixed point problem

    .. math:: \\mathrm{Find}\\, x:\\, x = Ax,

    where :math:`A` is a :math:`1/\gamma`-contractive operator, i.e. a :math:`L`-Lipschitz operator with :math:`L=1/\gamma`.

    This code computes a worst-case guarantee for the **Optimal Contractive Halpern Iteration**.
    That is, it computes the smallest possible :math:`\\tau(n, \\gamma)` such that the guarantee

    .. math:: \\|x_n - Ax_n\\|^2 \\leqslant \\tau(n, \\gamma) \\|x_0 - x_\\star\\|^2

    is valid, where :math:`x_n` is the output of the **Optimal Contractive Halpern iteration**,
    and :math:`x_\\star` is the fixed point of :math:`A`. In short, for a given value of :math:`n, \\gamma`,
    :math:`\\tau(n, \\gamma)` is computed as the worst-case value of
    :math:`\\|x_n - Ax_n\\|^2` when :math:`\\|x_0 - x_\\star\\|^2 \\leqslant 1`.

    **Algorithm**: The Optimal Contractive Halpern iteration can be written as

        .. math:: x_{t+1} = \\left(1 - \\frac{1}{\\varphi_{t+1}} \\right) Ax_t + \\frac{1}{\\varphi_{t+1}} x_0.

    where :math:`\\varphi_k = \sum_{i=0}^k \gamma^{2i}` and :math:`x_0` is a starting point.

    **Theoretical guarantee**: A **tight** worst-case guarantee for the Optimal Contractive Halpern iteration can be found in [1, Corollary 3.3, Theorem 4.1]:

        .. math:: \\|x_n - Ax_n\\|^2 \\leqslant \\left(1 + \\frac{1}{\\gamma}\\right)^2 \\left( \\frac{1}{\\sum_{k=0}^n \\gamma^k} \\right)^2 \\|x_0 - x_\\star\\|^2.

    **References**: The detailed approach and tight bound are available in [1].

    `[1] J. Park, E. Ryu (2022). Exact Optimal Accelerated Complexity for Fixed-Point Iterations. In 39th International Conference on Machine Learning (ICML).
    <https://proceedings.mlr.press/v162/park22c/park22c.pdf>`_

    Args:
        n (int): number of iterations.
        gamma (float): :math:`\\gamma \ge 1`. :math:`A` will be :math:`1/\\gamma`-contractive.
        verbose (int): Level of information details to print.
                        
                        - -1: No verbose at all.
                        - 0: This example's output.
                        - 1: This example's output + PEPit information.
                        - 2: This example's output + PEPit information + CVXPY details.

    Returns:
        pepit_tau (float): worst-case value
        theoretical_tau (float): theoretical value

    Example:
        >>> pepit_tau, theoretical_tau = wc_optimal_contractive_halpern_iteration(n=10, gamma=1.1, verbose=1)
        (PEPit) Setting up the problem: size of the main PSD matrix: 13x13
        (PEPit) Setting up the problem: performance measure is minimum of 1 element(s)
        (PEPit) Setting up the problem: Adding initial conditions and general constraints ...
        (PEPit) Setting up the problem: initial conditions and general constraints (1 constraint(s) added)
        (PEPit) Setting up the problem: interpolation conditions for 1 function(s)
                         function 1 : Adding 132 scalar constraint(s) ...
                         function 1 : 132 scalar constraint(s) added
        (PEPit) Compiling SDP
        (PEPit) Calling SDP solver
        (PEPit) Solver status: optimal (solver: SCS); optimal value: 0.010613882599724987
        *** Example file: worst-case performance of Optimal Contractive Halpern Iterations ***
                PEPit guarantee:         ||xN - AxN||^2 <= 0.0106139 ||x0 - x_*||^2
                Theoretical guarantee:   ||xN - AxN||^2 <= 0.0106132 ||x0 - x_*||^2

    """

    # Instantiate PEP
    problem = PEP()

    # Declare a non expansive operator
    A = problem.declare_function(LipschitzOperator, L=1 / gamma)

    # Start by defining its unique optimal point xs = x_*
    xs, _, _ = A.fixed_point()

    # Then define the starting point x0 of the algorithm
    x0 = problem.set_initial_point()

    # Set the initial constraint that is the difference between x0 and xs
    problem.set_initial_condition((x0 - xs) ** 2 <= 1)

    # Run n steps of Optimal Contractive Halpern Iterations
    x = x0
    for i in range(n):
        phi = (gamma ** (2 * i + 4) - 1) / (gamma ** 2 - 1)
        x = 1 / phi * x0 + (1 - 1 / phi) * A.gradient(x)

    # Set the performance metric to distance between xN and AxN
    problem.set_performance_metric((x - A.gradient(x)) ** 2)

    # Solve the PEP
    pepit_verbose = max(verbose, 0)
    pepit_tau = problem.solve(verbose=pepit_verbose)

    # Compute theoretical guarantee (for comparison)
    theoretical_tau = (1 + 1 / gamma) ** 2 * ((gamma - 1) / (gamma ** (n + 1) - 1)) ** 2

    # Print conclusion if required
    if verbose != -1:
        print('*** Example file: worst-case performance of Optimal Contractive Halpern Iterations ***')
        print('\tPEPit guarantee:\t ||xN - AxN||^2 <= {:.6} ||x0 - x_*||^2'.format(pepit_tau))
        print('\tTheoretical guarantee:\t ||xN - AxN||^2 <= {:.6} ||x0 - x_*||^2'.format(theoretical_tau))

    # Return the worst-case guarantee of the evaluated method (and the reference theoretical value)
    return pepit_tau, theoretical_tau


if __name__ == "__main__":
    pepit_tau, theoretical_tau = wc_optimal_contractive_halpern_iteration(n=10, gamma=1.1, verbose=1)
