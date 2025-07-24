def deal_return_MindSpore(frame, version, op, Return):
    print('merge (: return {framework: "%s", version: "%s", operator: "%s", description: "%s"});' % (
        frame, version, op, Return))
    print('match')
    print(' (m11: operator {framework: "%s", full_name: "%s", version: "%s"}),' % (frame, op, version))
    print(' (n11: return)')
    print('where n11.operator = "%s" and n11.framework = "%s" and n11.version = "%s"' % (op, frame, version))
    print('merge (m11) -[: returnOfOperator {name: "return", framework: "%s", version: n11.version}] -> (n11);' % (frame))

def deal_op(frame, version, name, type, desc, args_list, Raises, Supported_Platforms):
    classes = name.split('.')
    print('merge (: framework {name: "%s", version: "%s"});' % (frame, version))
    for i in range(len(classes) - 1):
        clas = classes[i]
        print('merge (: module {framework: "%s", name: "%s", version: "%s"});' % (frame, clas, version))
        if i == 0:
            print('match')
            print(' (m1: framework {name: "%s", version: "%s"}),' % (frame, version))
            print(' (m2: module {framework: "%s", name: "%s", version: "%s"})' % (frame, clas, version))
            print('merge (m1) -[: classOfFramework {name: "%s"}]-> (m2);' % clas)
        else:
            print('match')
            print(' (m1: module {framework: "%s", name: "%s", version: "%s"}),' % (frame, classes[i - 1], version))
            print(' (m2: module {framework: "%s", name: "%s", version: "%s"})' % (frame, clas, version))
            print('merge (m1) -[: subClassOfClass {name: "%s"}]-> (m2);' % clas)
    print('merge (: operator {framework: "%s", name: "%s", full_name: "%s", version: "%s", type: "%s", description:  "%s", args_list: "%s", supported_platforms: "%s", raises: "%s"});' % (
        frame, classes[-1], name, version, type, desc, args_list, Supported_Platforms, Raises))
    print('match')
    print(' (m3: module {framework: "%s", name: "%s", version: "%s"}),' % (frame, classes[-2], version))
    print(' (m4: operator {framework: "%s", name: "%s", full_name: "%s", version: "%s"})' % (
        frame, classes[-1], name, version))
    print('merge (m3) -[: operatorOfClass {name: "%s"}]-> (m4);' % (classes[-1]))
