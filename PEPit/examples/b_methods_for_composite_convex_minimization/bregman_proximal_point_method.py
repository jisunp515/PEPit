from PEPit.pep import PEP
from PEPit.functions.convex_function import ConvexFunction
from PEPit.primitive_steps.bregman_proximal_step import bregman_proximal_step


def wc_bpp(gamma, n, verbose=True):
    """
    Consider the composite convex minimization problem

        .. math:: \min_x \\{F(x) \equiv f_1(x)+f_2(x) \\}

    where :math:`f_1(x)` and :math:`f_2(x)` are closed convex proper functions.

    This code computes a worst-case guarantee for **Bregman Proximal Point** method.
    That is, it computes the smallest possible :math:`\\tau(n, \\gamma)` such that the guarantee

        .. math:: F(x_n) - F(x_\star) \\leqslant \\tau(n, \gamma) D_h(x_\star,x_0)

    is valid, where :math:`x_n` is the output of the **Bregman Proximal Point** method,
    where :math:`x_\star` is a minimizer of :math:`F`, when :math:`Dh` is the Bregman distance generated by :math:`h`.

    **Algorithm**:

        .. math:: x_{t+1} = \\arg\\min_{u \\in R^n} \\nabla f(x_t)^T(u - x_t) + \\frac{1}{\\gamma} D_h(u, x_t)

        .. math:: D_h(x, y) = h(x) - h(y) - \\nabla h (y)^T(x - y)

    **Theoretical guarantee**:

    The **tight** guarantee is obtained in [1, Theorem 1]

        .. math:: F(x_n) - F(x_\star) \\leqslant \\frac{1}{\\gamma n} D_h(x_\star,x_0)

    **References**:

    The detailed approach (based on convex relaxations) is available in [1, Theorem 1]

    [1] Radu-Alexandru Dragomir, Adrien B. Taylor, Alexandre d’Aspremont, and
    Jérôme Bolte. "Optimal Complexity and Certification of Bregman
    First-Order Methods". (2019)

    Args:
        gamma (float): step size.
        n (int): number of iterations.
        verbose (bool, optional): if True, print conclusion

    Returns:
        tuple: worst_case value, theoretical value

    Examples:
        >>> pepit_tau, theoretical_tau = wc_bpp(3,5)
        (PEP-it) Setting up the problem: size of the main PSD matrix: 20x20
        (PEP-it) Setting up the problem: performance measure is minimum of 1 element(s)
        (PEP-it) Setting up the problem: initial conditions (1 constraint(s) added)
        (PEP-it) Setting up the problem: interpolation conditions for 3 function(s)
                 function 1 : 30 constraint(s) added
                 function 2 : 30 constraint(s) added
                 function 3 : 42 constraint(s) added
        (PEP-it) Compiling SDP
        (PEP-it) Calling SDP solver
        (PEP-it) Solver status: optimal (solver: SCS); optimal value: 0.06666565028473753
        *** Example file: worst-case performance of the Bregman Proximal Point in function values ***
            PEP-it guarantee:	 f(x_n)-f_* <= 0.0666657 Dh(x0,xs)
            Theoretical guarantee :	 f(x_n)-f_* <= 0.0666667 Dh(x0,xs)
    """

    # Instantiate PEP
    problem = PEP()

    # Declare three convex functions
    func1 = problem.declare_function(ConvexFunction,
                                     param={})
    func2 = problem.declare_function(ConvexFunction,
                                     param={})
    h = problem.declare_function(ConvexFunction,
                                 param={})
    # Define the function to optimize as the sum of func1 and func2
    func = func1 + func2

    # Start by defining its unique optimal point xs = x_* and its function value fs = F(x_*)
    xs = func.stationary_point()
    fs = func.value(xs)
    ghs, hs = h.oracle(xs)

    # Then define the starting point x0 of the algorithm and its function value f0
    x0 = problem.set_initial_point()
    gh0, h0 = h.oracle(x0)

    # Set the initial constraint that is the Bregman distance between x0 and x^*
    problem.set_initial_condition(hs - h0 - gh0 * (xs - x0) <= 1)

    # Compute n steps of the Bregman Proximal Point method starting from x0
    gh = gh0
    for i in range(n):
        x, gh, hx, gx, ff = bregman_proximal_step(gh, h, func, gamma)

    # Set the performance metric to the final distance in function values to optimum
    problem.set_performance_metric(ff - fs)

    # Solve the PEP
    pepit_tau = problem.solve(verbose=verbose)

    # Compute theoretical guarantee (for comparison)
    theoretical_tau = 1 / gamma / n

    # Print conclusion if required
    if verbose:
        print('*** Example file: worst-case performance of the Bregman Proximal Point in function values ***')
        print('\tPEP-it guarantee:\t f(x_n)-f_* <= {:.6} Dh(x0,xs)'.format(pepit_tau))
        print('\tTheoretical guarantee :\t f(x_n)-f_* <= {:.6} Dh(x0,xs) '.format(theoretical_tau))
    # Return the worst-case guarantee of the evaluated method (and the upper theoretical value)
    return pepit_tau, theoretical_tau


if __name__ == "__main__":
    gamma = 3
    n = 5

    pepit_tau, theoretical_tau = wc_bpp(gamma=gamma,
                                        n=n)
