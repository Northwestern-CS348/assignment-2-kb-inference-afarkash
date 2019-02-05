import read, copy
from util import *
from logical_classes import *

verbose = 0

class KnowledgeBase(object):
    def __init__(self, facts=[], rules=[]):
        self.facts = facts
        self.rules = rules
        self.ie = InferenceEngine()

    def __repr__(self):
        return 'KnowledgeBase({!r}, {!r})'.format(self.facts, self.rules)

    def __str__(self):
        string = "Knowledge Base: \n"
        string += "\n".join((str(fact) for fact in self.facts)) + "\n"
        string += "\n".join((str(rule) for rule in self.rules))
        return string

    def _get_fact(self, fact):
        """INTERNAL USE ONLY
        Get the fact in the KB that is the same as the fact argument

        Args:
            fact (Fact): Fact we're searching for

        Returns:
            Fact: matching fact
        """
        for kbfact in self.facts:
            if fact == kbfact:
                return kbfact

    def _get_rule(self, rule):
        """INTERNAL USE ONLY
        Get the rule in the KB that is the same as the rule argument

        Args:
            rule (Rule): Rule we're searching for

        Returns:
            Rule: matching rule
        """
        for kbrule in self.rules:
            if rule == kbrule:
                return kbrule

    def kb_add(self, fact_rule):
        """Add a fact or rule to the KB
        Args:
            fact_rule (Fact|Rule) - the fact or rule to be added
        Returns:
            None
        """
        printv("Adding {!r}", 1, verbose, [fact_rule])
        if isinstance(fact_rule, Fact):
            if fact_rule not in self.facts:
                self.facts.append(fact_rule)
                for rule in self.rules:
                    self.ie.fc_infer(fact_rule, rule, self)
            else:
                if fact_rule.supported_by:
                    ind = self.facts.index(fact_rule)
                    for f in fact_rule.supported_by:
                        self.facts[ind].supported_by.append(f)
                else:
                    ind = self.facts.index(fact_rule)
                    self.facts[ind].asserted = True
        elif isinstance(fact_rule, Rule):
            if fact_rule not in self.rules:
                self.rules.append(fact_rule)
                for fact in self.facts:
                    self.ie.fc_infer(fact, fact_rule, self)
            else:
                if fact_rule.supported_by:
                    ind = self.rules.index(fact_rule)
                    for f in fact_rule.supported_by:
                        self.rules[ind].supported_by.append(f)
                else:
                    ind = self.rules.index(fact_rule)
                    self.rules[ind].asserted = True

    def kb_assert(self, fact_rule):
        """Assert a fact or rule into the KB

        Args:
            fact_rule (Fact or Rule): Fact or Rule we're asserting
        """
        fact_rule.asserted = True;
        printv("Asserting {!r}", 0, verbose, [fact_rule])
        self.kb_add(fact_rule)

    def kb_ask(self, fact):
        """Ask if a fact is in the KB

        Args:
            fact (Fact) - Statement to be asked (will be converted into a Fact)

        Returns:
            listof Bindings|False - list of Bindings if result found, False otherwise
        """
        print("Asking {!r}".format(fact))
        if factq(fact):
            f = Fact(fact.statement)
            bindings_lst = ListOfBindings()
            # ask matched facts
            for fact in self.facts:
                binding = match(f.statement, fact.statement)
                if binding:
                    bindings_lst.add_bindings(binding, [fact])

            return bindings_lst if bindings_lst.list_of_bindings else []

        else:
            print("Invalid ask:", fact.statement)
            return []

    def kb_retract(self, fact_or_rule):
        """Retract a fact from the KB

        Args:
            fact (Fact) - Fact to be retracted

        Returns:
            None
        """
        printv("Retracting {!r}", 0, verbose, [fact_or_rule])
        ####################################################
        # Student code goes here
        
        if( (factq(fact_or_rule)) and (fact_or_rule in self.facts)): #if it is a fact in the knowledge base, get it
            fact2Del = self._get_fact(fact_or_rule)                  
            
            if(len(fact2Del.supported_by) == 0):                     #if it is not supported by anything, remove it
                self.facts.remove(fact2Del)
                                                                     #remove all facts that it is the sole supporter of
                for factSupported in fact2Del.supports_facts:
                    for ff in factSupported.supported_by:
                        if fact_or_rule in ff:
                            self._get_fact(factSupported).supported_by.remove(ff)
                        
                    self.kb_retract(factSupported)
                    
                    
                for ruleSupported in fact2Del.supports_rules:        #remove all rules that it is the sole supporter of
                    for rr in ruleSupported.supported_by:
                        if fact_or_rule in rr:
                            self._get_rule(ruleSupported).supported_by.remove(rr)
                    
                    self.kb_retract(ruleSupported)
                    
            else:
                fact2Del.asserted == False                           #if fact was originally asserted and supported, set asserted to False
             
        elif( (isinstance(fact_or_rule, Rule)) and (fact_or_rule in self.rules)):   #if it is a rule in the knowledge base, get it
            rule2Del = self._get_rule(fact_or_rule)
            
            if( (rule2Del.asserted == False) or (len(rule2Del.supported_by) == 0)): #if it is not supported by anything, remove it
                self.rules.remove(rule2Del)

                for ruleSupported in rule2Del.supports_rules:                       #remove all rules that it is the sole supporter of
                    for rr in ruleSupported.supported_by:
                        if fact_or_rule in rr:
                            self._get_rule(ruleSupported).supported_by.remove(rr)
                    
                    self.kb_retract(ruleSupported)
                                                                                   #remove all facts that it is the sole supporter of                             
                for factSupported in rule2Del.supports_facts:
                    for ff in factSupported.supported_by:
                        if fact_or_rule in ff:
                            self._get_fact(factSupported).supported_by.remove(ff)                    
                    
                    #self.kb_retract(factSupported)
        else: 
            return
 
        

class InferenceEngine(object):
    def fc_infer(self, fact, rule, kb):
        """Forward-chaining to infer new facts and rules

        Args:
            fact (Fact) - A fact from the KnowledgeBase
            rule (Rule) - A rule from the KnowledgeBase
            kb (KnowledgeBase) - A KnowledgeBase

        Returns:
            Nothing            
        """
        printv('Attempting to infer from {!r} and {!r} => {!r}', 1, verbose,
            [fact.statement, rule.lhs, rule.rhs])
        ####################################################
        # Student code goes here
        '''
        use util.match to do unification and create possible bindings
        use util.instantiate to bind a virabile in the rest of a rule
        For rule R, fact F, and inferred fact/rule fr,
        add R and F to 'supported by' in fr
        add rf to 'supports rules' or 'supports facts' in R and F
        
        '''
       
        newBindings = match(rule.lhs[0], fact.statement)
        
        if newBindings != False:
            state = instantiate(rule.rhs, newBindings)
            if len(rule.lhs) == 1:
                newFact = Fact(statement=state, supported_by=[(fact, rule)])
                newFact.asserted = False
                
                
                fact.supports_facts.append(newFact)
                rule.supports_facts.append(newFact)                
                kb.kb_add(newFact)                
                
            else:
                newLHS = []
                for condition in rule.lhs[1:]:
                    newLHS.append(instantiate(condition, newBindings))
                newRule = Rule([newLHS, state], supported_by=[(fact, rule)])
                newRule.asserted = False;
                
                fact.supports_rules.append(newRule)
                rule.supports_rules.append(newRule)
                kb.kb_add(newRule)                
            return
        return
