import math
from .optimizer import Optimizer

class Rprop(Optimizer):

    def __init__(self, params, lr=1e-2, etas=(0.5, 1.2), step_sizes=(1e-6, 50)):
        defaults = dict(lr=lr, etas=etas, step_sizes=step_sizes)
        super(Rprop, self).__init__(params, defaults)

    def step(self, closure=None):
        loss = None
        if closure is not None:
            loss = closure()

        for group in self.param_groups:
            for p in group['params']:
                grad = p.grad
                state = self.state[id(p)]

                # State initialization
                if len(state) == 0:
                    state['step'] = 0
                    state['prev'] = grad.new().resize_as_(grad).zero_()
                    state['step_size'] = grad.new().resize_as_(grad).fill_(group['lr'])

                etaminus, etaplus = group['etas']
                step_size_min, step_size_max = group['step_sizes']
                step_size = state['step_size']

                state['step'] += 1

                sign = grad.mul(state['prev']).sign()
                sign[sign.gt(0)] = etaplus
                sign[sign.lt(0)] = etaminus
                sign[sign.eq(0)] = 1

                # update stepsizes with step size updates
                step_size.mul_(sign).clamp_(step_size_min, step_size_max)

                # for dir<0, dfdx=0
                # for dir>=0 dfdx=dfdx
                grad = grad.clone()
                grad[sign.eq(etaminus)] = 0

                # update parameters
                p.data.addcmul_(-1, grad.sign(), step_size)

                state['prev'].copy_(grad)

        return loss
