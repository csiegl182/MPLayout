import xml.dom.minidom as xml
import numpy as np
import os

# parsing functions
def find_first_element_with_attribute(root, tag, attribute, value):
    elements = root.getElementsByTagName(tag)
    for element in elements:
        if element.getAttribute(attribute) == value:
            return element

def get_path_element(root, id):
    g_element = find_first_element_with_attribute(root, 'g', 'id', id)
    return g_element.getElementsByTagName('path')[0]

def get_path_values(root, id):
    if type(id) == list:
        return [get_path_element(root, i).getAttribute('d') for i in id]
    else:
        return get_path_element(root, id).getAttribute('d')

def insert_animation(parent, animation_tag):
    parent.appendChild(animation_tag)

def create_animate_tag(root, attributeName, values, duration, id="", calcMode="discrete", repeatCount="indefinite"):
    if type(duration) == int or type(duration) == float:
        duration = str(duration)+'s'
    animate_tag = root.createElement('animate')
    animate_tag.setAttribute("id", id)
    animate_tag.setAttribute("attributeName", attributeName)
    animate_tag.setAttribute("values", values)
    animate_tag.setAttribute("dur", duration)
    animate_tag.setAttribute("calcMode", calcMode)
    animate_tag.setAttribute("repeatCount", repeatCount)
    return animate_tag

def insert_animate_tag(id, get_target_path_element, get_element_path_values, get_reference_path_values, create_path_values, create_animate_tag):
    target_element = get_target_path_element()
    elem_path = get_element_path_values()
    ref_path = get_reference_path_values()
    path_values = create_path_values(elem_path, ref_path)

    animate_tag = create_animate_tag(
        id=id,
        attributeName="d",
        values = ';'.join(path_values))

    insert_animation(target_element, animate_tag)

# animation functions
def get_path_x(path, dtype=float):
    path = path.split()
    return np.array([p for p in path[1::3]], dtype=dtype)

def get_path_y(path, dtype=float):
    path = path.split()
    return np.array([p for p in path[2::3]], dtype=dtype)

def get_path_xy(path, dtype=float):
    return np.array([[x, y] for x, y in zip(get_path_x(path, dtype=dtype), get_path_y(path, dtype=dtype))])

def resample(vec, N):
    if len(vec) > N:
        return vec[np.array(np.rint(np.linspace(0, len(vec)-1, N)), dtype=int)]
    else:
        print("Waring: Inaccurate resampling: Reference length {} < desired length {}".format(len(vec), N))
        return vec

def reveal_path(elem_path, _, N):
    elem_path = elem_path.split()
    elem_path = [' '.join(elem_path[i:i+3]) for i in range(0, len(elem_path), 3)]
    return [' '.join(elem_path[0:i+1]) for i in np.array(np.rint(np.linspace(0, len(elem_path)-1, N)), dtype=int)]

def move_stem(elem_path, ref_path, N):
    elem_path = elem_path.split()
    xy_ref = resample(get_path_xy(ref_path, dtype=str), N)
    return [' '.join([elem_path[0], xy[0]] + elem_path[2:4] + list(xy)) for xy in xy_ref]

def move_along_path(elem_path, ref_path, N):
    ref_path = ref_path.split()
    ref_values = [float(x) for x in ref_path if x.replace('.', '').isnumeric()]
    ref_values = [[ref_values[i], ref_values[i+1]] for i in range(0, len(ref_values), 2)]
    p_end = ref_values[-1]
    ref_values = resample(np.array(ref_values), N)

    elem_values0 = ''.join([c for c in elem_path if not c.isalpha()]).split()
    elem_values0 = [float(ev) for ev in elem_values0]
    elem_values0 = [(elem_values0[i], elem_values0[i+1]) for i in range(0, len(elem_values0), 2)]
    elem_values0 = [(ev[0]-p_end[0], ev[1]-p_end[1]) for ev in elem_values0]

    elem_path = elem_path.split()
    path = []
    for rv in ref_values:
        evx = [ev[0]+rv[0] for ev in elem_values0]
        evy = [ev[1]+rv[1] for ev in elem_values0]
        elem_values = [j for i in zip(evx,evy) for j in i]

        for i, ep in enumerate(elem_path):
            if ep.isalpha():
                elem_values.insert(i, ep)

        elem_values = [str(ev) for ev in elem_values]
        elem_values = ' '.join(elem_values)

        path.append(elem_values)
    return path

def static_stem(elem_path, ref_path, N):
    elem_path = elem_path.split()
    y_ref = resample(get_path_y(ref_path, dtype=str), N)
    return [' '.join(elem_path[:-1] + [y]) for y in y_ref]

def move_along_y_path(elem_path, ref_path, N):
    def add_y_value(path, y):
        path = [float(ep) if not ep.isalpha() else ep for ep in path]
        y_value = False
        for i in range(len(path)):
            if type(path[i]) == str: continue
            if y_value:
                path[i] += y
                y_value = False
            else:
                y_value = True
        return [str(ep) for ep in path]

    y_ref = resample(get_path_y(ref_path), N)
    y0 = y_ref[0]
    elem_path = elem_path.split()
    return [' '.join(add_y_value(elem_path, y-y0)) for y in y_ref]

def rotate_path_with_two_points(elem_path, ref_path, N):
    elem_path = elem_path.split()
    p1 = np.matrix([float(p) for p in elem_path[1:3]]).T
    p2 = np.matrix([float(p) for p in elem_path[-2:]]).T
    d = p2-p1
    r = np.sqrt(d.T*d).item()

    y_ref = get_path_y(ref_path)
    y_ref -= np.mean(y_ref)
    y_ref /= max(abs(y_ref))
    y_ref = resample(y_ref, N)

    x_ref = np.sqrt(1-y_ref**2)

    x_sign = -np.sign(np.diff(y_ref))
    x_sign = np.append(x_sign, x_sign[-1])
    x_ref *= x_sign
    x_ref *= r
    x_ref += p1[0].item()
    y_ref *= r
    y_ref += p1[1].item()

    path_values = [' '.join(elem_path[:4] + [str(x), str(y)]) for x, y in zip(x_ref, y_ref)]
    return path_values

def move_projection(elem_path, ref_path, N):
    elem_path = elem_path.split()
    x0 = float(elem_path[1])

    y_ref = get_path_y(ref_path)
    y0 = np.mean(y_ref)
    y_ref -= y0
    r = max(abs(y_ref))
    y_ref /= r
    y_ref = resample(y_ref, N)

    x_ref = np.sqrt(1-y_ref**2)
    x_sign = -np.sign(np.diff(y_ref))
    x_sign = np.append(x_sign, x_sign[-1])
    x_ref *= x_sign
    x_ref *= r
    x_ref += x0
    x_ref = [str(x) for x in x_ref]
    y_ref *= r
    y_ref += y0
    y_ref = [str(y) for y in y_ref]

    path_values = [elem_path[:2] + [y] + elem_path[3:4] + [x] + [y] for x, y in zip(x_ref, y_ref)]
    path_values = [' '.join(pv) for pv in path_values]
    return path_values

def rotate_polygon(elem_path, ref_path, N):
    def get_center(ref_path):
        ref_path = ref_path.split()
        center = [float(x) for x in ref_path[1:3]]
        return np.matrix(center).transpose()

    ref_phasor = ref_path[1]
    ref_path = ref_path[0]

    elem_path = elem_path.split()
    p_poly = np.hstack([np.matrix([x, y], dtype=float).T for x,y in zip(elem_path[1::3], elem_path[2::3])])
    t_poly = [t for t in elem_path[::3]]

    p0 = get_center(ref_phasor)
    p_poly0 = p_poly-p0
    phi0 = np.mean(np.arctan2(p_poly0[1,:], p_poly0[0,:]))

    y_ref = get_path_y(ref_path)
    y_ref -= np.mean(y_ref)
    y_ref /= max(abs(y_ref))
    y_ref = resample(y_ref, N)

    x_ref = np.sqrt(1-y_ref**2)
    x_sign = -np.sign(np.diff(y_ref))
    x_sign = np.append(x_sign, x_sign[-1])
    x_ref *= x_sign
    phi_vec = np.arctan2(y_ref, x_ref)
    phi_vec -= phi0

    A = lambda phi: np.matrix([[np.cos(phi), -np.sin(phi)], [np.sin(phi), np.cos(phi)]])

    poly_values = [np.array(A(phi)*p_poly0 + p0) for phi in phi_vec]
    poly_values = [ [' '.join([t, str(p[0]), str(p[1])]) for t, p in zip(t_poly, pv.T)] for pv in poly_values]
    poly_values = [' '.join(pv) for pv in poly_values]
    return poly_values

# create anim configuration
def animation_config(id, duration_s, N_points, create_path_values, ref_id=None):
    config = {
        'id': id,
        'duration': duration_s,
        'N': N_points,
        'create_path_values': create_path_values
    }
    if ref_id is not None:
        config['reference_path_id'] = ref_id
    return [config]

# handle svg files
def create_document(filename):
    return xml.parse(filename)

def animate_path_caller(
        svg,
        id,
        N,
        duration,
        create_path_values,
        get_target_path_element=get_path_element,
        get_element_path_values=get_path_values,
        reference_path_id=None,
        get_reference_path_values=get_path_values,
        create_animate_tag=create_animate_tag):
    insert_animate_tag(
        id=id+'_animate',
        get_target_path_element=lambda : get_target_path_element(svg, id),
        get_element_path_values=lambda : get_element_path_values(svg, id),
        get_reference_path_values=lambda : get_reference_path_values(svg, id if reference_path_id==None else reference_path_id),
        create_path_values=lambda elem_path, ref_path: create_path_values(elem_path, ref_path, N),
        create_animate_tag=lambda **kwargs: create_animate_tag(svg, duration=duration, **kwargs)
    )

def execute_config_set_on_svg(svg, animation_config_set):
    for config in animation_config_set:
        try:
            animate_path_caller(svg, **config)
        except:
            print('Could not create animation with id {}'.format(config['id']))

def pretty_file_size(file_size):
    for size_tag in ['B', 'kB', 'MB', 'GB', 'TB']:
        if file_size < 1000:
            break
        file_size /= 1024
    return str(round(file_size))+size_tag

def animate_svg(svg_file, animation_config_set):
    print('Original file size: {}'.format(pretty_file_size(os.path.getsize(svg_file))))
    svg = create_document(svg_file)
    execute_config_set_on_svg(svg, animation_config_set)
    with open(svg_file, 'w') as f:
        f.write(svg.toxml())
    print('Animated file size: {}'.format(pretty_file_size(os.path.getsize(svg_file))))
