"""YAML Anchor/Alias Optimizer Utility Tests"""

# *** imports

# ** infra
import yaml

# ** app
from ..core import Rewrite
from ..optimizer import OPTIMIZER_REWRITE_SET, YamlAnchorOptimizer

# *** classes

# ** class: _other_envelope_rewrite
class _OtherEnvelopeRewrite(Rewrite):
    '''
    A test rewrite that records two locations under a third envelope key.
    '''

    # * method: apply
    def apply(self, candidate, context):
        '''
        Record two locations so optimize shares one list without a built-in key.

        :param candidate: The other-envelope dict.
        :type candidate: dict
        :param context: The rewrite visit context.
        :type context: RewriteContext
        :return: None
        :rtype: None
        '''

        # Two locations force a shared canonical list through the unchanged optimize path.
        fingerprint = ('marked', ('shared',))
        locations = context.accumulator.setdefault(fingerprint, [])
        locations.append((candidate, 'left'))
        locations.append((candidate, 'right'))
        return None

# *** tests

# ** test: optimizer_rewrite_set_order
def test_optimizer_rewrite_set_order() -> None:
    '''
    Test that the default rewrite set is the three rows in envelope-then-callable order.
    '''

    # Zero-arg construction uses the module set so DI does not need a factory argument.
    optimizer = YamlAnchorOptimizer()
    assert optimizer.rewrites is OPTIMIZER_REWRITE_SET

    # evt_grp precedes cmpt so a dual-emitted document prefers the legacy envelope.
    assert [rewrite.id for rewrite in OPTIMIZER_REWRITE_SET] == [
        'optimizer.evt_grp_envelope',
        'optimizer.cmpt_envelope',
        'optimizer.callable',
    ]
    assert [rewrite.applies_to for rewrite in OPTIMIZER_REWRITE_SET] == [
        'evt_grp',
        'cmpt',
        'callable',
    ]

# ** test: no_events_passthrough
def test_no_events_passthrough() -> None:
    '''
    Test that an envelope with no callables is returned unchanged.
    '''

    # A named envelope with no events has nothing to collect.
    codegen = {'evt_grp': {'name': 'error'}}
    result = YamlAnchorOptimizer().optimize(codegen)

    # The same object is returned and vars is not invented.
    assert result is codegen
    assert 'vars' not in result

# ** test: single_event_no_anchors
def test_single_event_no_anchors() -> None:
    '''
    Test that one event's unique params and returns stay in place.
    '''

    # One execute callable owns both lists.
    params = ['id:str:true::']
    returns = ['Feature:']
    codegen = {
        'evt_grp': {
            'evts': {
                'GetFeature': {
                    'execute': {
                        'params': params,
                        'returns': returns,
                    },
                },
            },
        },
    }

    # Unique lists are not replaced and vars is omitted.
    result = YamlAnchorOptimizer().optimize(codegen)
    execute = result['evt_grp']['evts']['GetFeature']['execute']
    assert result is codegen
    assert execute['params'] is params
    assert execute['returns'] is returns
    assert 'vars' not in result

# ** test: multiple_events_params_anchored
def test_multiple_events_params_anchored() -> None:
    '''
    Test that identical params lists on two events share one object under vars.
    '''

    # Equal contents, distinct objects, so sharing is the optimizer's work.
    left_params = ['id:str:true::', 'name:str:false::']
    right_params = ['id:str:true::', 'name:str:false::']
    codegen = {
        'evt_grp': {
            'evts': {
                'GetA': {
                    'execute': {
                        'params': left_params,
                        'returns': ['A:'],
                    },
                },
                'GetB': {
                    'execute': {
                        'params': right_params,
                        'returns': ['B:'],
                    },
                },
            },
        },
    }

    # Both parents and vars point at the same canonical list.
    result = YamlAnchorOptimizer().optimize(codegen)
    shared = result['evt_grp']['evts']['GetA']['execute']['params']
    assert list(result)[0] == 'vars'
    assert shared is result['evt_grp']['evts']['GetB']['execute']['params']
    assert shared is result['vars'][0]
    assert shared == left_params
    assert result['evt_grp']['evts']['GetA']['execute']['returns'] is not (
        result['evt_grp']['evts']['GetB']['execute']['returns']
    )

    # Shared identity is what lets PyYAML emit an anchor and an alias.
    text = yaml.dump(result, default_flow_style=False, sort_keys=False)
    assert '&' in text
    assert '*' in text

# ** test: multiple_events_returns_anchored
def test_multiple_events_returns_anchored() -> None:
    '''
    Test that identical returns lists on two events share one object.
    '''

    # Returns match; params do not, so only the returns fingerprint is shared.
    left_returns = ['Feature:', 'bool:']
    right_returns = ['Feature:', 'bool:']
    codegen = {
        'evt_grp': {
            'evts': {
                'GetA': {
                    'execute': {
                        'params': ['id:str:true::'],
                        'returns': left_returns,
                    },
                },
                'GetB': {
                    'execute': {
                        'params': ['name:str:true::'],
                        'returns': right_returns,
                    },
                },
            },
        },
    }

    # The returns list is shared; the distinct params lists stay put.
    result = YamlAnchorOptimizer().optimize(codegen)
    shared = result['evt_grp']['evts']['GetA']['execute']['returns']
    assert shared is result['evt_grp']['evts']['GetB']['execute']['returns']
    assert shared is result['vars'][0]
    assert shared == left_returns
    assert result['evt_grp']['evts']['GetA']['execute']['params'] is not (
        result['evt_grp']['evts']['GetB']['execute']['params']
    )

# ** test: vars_not_present_without_duplicates
def test_vars_not_present_without_duplicates() -> None:
    '''
    Test that distinct lists across two events do not add vars.
    '''

    # Two events whose lists differ in every fingerprint.
    codegen = {
        'evt_grp': {
            'evts': {
                'GetA': {
                    'execute': {
                        'params': ['id:str:true::'],
                        'returns': ['A:'],
                    },
                },
                'GetB': {
                    'execute': {
                        'params': ['name:str:true::'],
                        'returns': ['B:'],
                    },
                },
            },
        },
    }

    # No duplicate means the input object is returned without vars.
    result = YamlAnchorOptimizer().optimize(codegen)
    assert result is codegen
    assert 'vars' not in result

# ** test: cmpt_envelope_functions_collected
def test_cmpt_envelope_functions_collected() -> None:
    '''
    Test that a cmpt-only document shares function params.
    '''

    # No evt_grp key, so the component envelope is the selected rewrite.
    codegen = {
        'cmpt': {
            'grps': [
                {
                    'evts': {},
                    'fncs': {
                        'build': {'params': ['id:str:true::'], 'returns': ['str:']},
                        'parse': {'params': ['id:str:true::'], 'returns': ['int:']},
                    },
                },
            ],
        },
    }

    # The empty evts payload is skipped and the two function params are shared.
    result = YamlAnchorOptimizer().optimize(codegen)
    functions = result['cmpt']['grps'][0]['fncs']
    assert functions['build']['params'] is functions['parse']['params']
    assert functions['build']['params'] is result['vars'][0]
    assert 'evt_grp' not in result

# ** test: cmpt_envelope_class_payloads_collected
def test_cmpt_envelope_class_payloads_collected() -> None:
    '''
    Test that class-shaped cmpt payloads collect execute and method lists.
    '''

    # clss and repos are both class-shaped; an empty mdls key must be skipped.
    codegen = {
        'cmpt': {
            'grps': [
                {
                    'mdls': {},
                    'clss': {
                        'Helper': {
                            'execute': None,
                            'methods': {
                                'check': {'params': ['id:str:true::'], 'returns': ['bool:']},
                            },
                        },
                        'Other': {
                            'methods': {
                                'check': {'params': ['id:str:true::'], 'returns': ['str:']},
                            },
                        },
                    },
                    'repos': {
                        'TokenRepo': {
                            'execute': {'params': ['key:str:true::'], 'returns': ['Token:']},
                        },
                        'OtherRepo': {
                            'execute': {'params': ['key:str:true::'], 'returns': ['None:']},
                        },
                    },
                },
            ],
        },
    }

    # Method params and execute params each become one shared object.
    result = YamlAnchorOptimizer().optimize(codegen)
    group = result['cmpt']['grps'][0]
    assert group['clss']['Helper']['methods']['check']['params'] is (
        group['clss']['Other']['methods']['check']['params']
    )
    assert group['repos']['TokenRepo']['execute']['params'] is (
        group['repos']['OtherRepo']['execute']['params']
    )
    assert len(result['vars']) == 2

# ** test: evt_grp_methods_collected
def test_evt_grp_methods_collected() -> None:
    '''
    Test that evt_grp collects method lists as well as execute lists.
    '''

    # Methods match; execute params do not.
    codegen = {
        'evt_grp': {
            'evts': {
                'GetA': {
                    'execute': {'params': ['id:str:true::']},
                    'methods': {
                        'check': {'params': ['flag:bool:true::']},
                    },
                },
                'GetB': {
                    'execute': {'params': ['name:str:true::']},
                    'methods': {
                        'check': {'params': ['flag:bool:true::']},
                    },
                },
            },
        },
    }

    # Only the method params fingerprint is shared.
    result = YamlAnchorOptimizer().optimize(codegen)
    methods = result['evt_grp']['evts']
    assert methods['GetA']['methods']['check']['params'] is (
        methods['GetB']['methods']['check']['params']
    )
    assert methods['GetA']['methods']['check']['params'] is result['vars'][0]

# ** test: evt_grp_ignores_module_functions
def test_evt_grp_ignores_module_functions() -> None:
    '''
    Test that evt_grp does not collect module-level functions.
    '''

    # Identical function params would anchor if this rewrite walked fncs.
    codegen = {
        'evt_grp': {
            'fncs': {
                'build': {'params': ['id:str:true::']},
                'parse': {'params': ['id:str:true::']},
            },
        },
    }

    # Module functions are left for the component envelope.
    result = YamlAnchorOptimizer().optimize(codegen)
    assert result is codegen
    assert 'vars' not in result

# ** test: dual_emitted_envelope_prefers_evt_grp
def test_dual_emitted_envelope_prefers_evt_grp() -> None:
    '''
    Test that a document with both envelopes collects evt_grp and skips cmpt.
    '''

    # cmpt has a duplicate the legacy envelope does not.
    codegen = {
        'evt_grp': {
            'evts': {
                'GetA': {'execute': {'params': ['id:str:true::']}},
            },
        },
        'cmpt': {
            'grps': [
                {
                    'fncs': {
                        'build': {'params': ['id:str:true::']},
                        'parse': {'params': ['id:str:true::']},
                    },
                },
            ],
        },
    }

    # The first matching rewrite wins, so the cmpt duplicate is not shared.
    result = YamlAnchorOptimizer().optimize(codegen)
    functions = result['cmpt']['grps'][0]['fncs']
    assert result is codegen
    assert 'vars' not in result
    assert functions['build']['params'] is not functions['parse']['params']

# ** test: third_envelope_key_attaches_without_optimizer_changes
def test_third_envelope_key_attaches_without_optimizer_changes() -> None:
    '''
    Test that a custom rewrite for another envelope key is selected by the existing dispatch.
    '''

    # The default set does not know this key, so it must leave the dict alone.
    untouched = {'other': {'left': ['old'], 'right': ['old']}}
    assert YamlAnchorOptimizer().optimize(untouched) is untouched

    # A custom set whose first hook is present is selected without editing optimize.
    codegen = {
        'other': {'left': ['old'], 'right': ['old']},
        'evt_grp': {'evts': {}},
    }
    optimizer = YamlAnchorOptimizer(rewrites=[
        _OtherEnvelopeRewrite(
            id='test.other',
            applies_to='other',
        ),
    ])
    collected = optimizer.collect_lists(codegen)
    assert ('marked', ('shared',)) in collected

    result = optimizer.optimize(codegen)
    assert result['other']['left'] is result['other']['right']
    assert result['other']['left'] is result['vars'][0]
    assert list(result)[0] == 'vars'
