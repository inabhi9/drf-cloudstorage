import ntpath
import re


def path_leaf(path):
    """
    Extracts file name from given path

    :param str path: Path be extracted the file name from
    :return str: File name
    """
    head, tail = ntpath.split(path)
    return tail or ntpath.basename(head)


def shorten_str(s, to_length=10, append=None):
    """
    Truncate string to a given length with appending 2 dots.

    :param str s:
    :param int to_length:
    :param str append: String to be appended after truncating the actual string.
    :return:
    """
    if len(s) > to_length:
        s = s[:to_length]
        if append:
            s = '%s..%s' % (s, append)
        return s
    else:
        return '%s%s' % (s, append or '')


class CloudinaryHelper(object):
    secure_url = None
    public_id = None
    version = None
    format = None

    def __init__(self, d):
        self._data = d
        for k, v in d.items():
            setattr(self, k, v)

        if self.format is None and '.' in self.public_id:
            self.format = self.public_id.split('.')[-1]

    @property
    def base_url(self):
        secure_url = self.secure_url
        image_path = '%s.%s' % (self.public_id, self.format)
        version = 'v%s' % self.version

        return secure_url.replace(version + '/' + image_path, '')

    @property
    def file_name(self):
        if '.' in self.public_id:
            return self.public_id.split('/')[-1]
        else:
            return '%s.%s' % (self.public_id.split('/')[-1], self.format)

    def edit(self, s):
        """
        Injects the edit path parameters `s` into the url

        :param str s: Cloudinary edit string
        :returns Url: injected `s` in to the secure url
        """
        # Fallback method to build edited url
        if not self.public_id:
            base_url, public_id = re.match(r'(.*)(v[0-9]+.*)', self.secure_url).groups()
            return '%s%s/%s' % (base_url, s, public_id)

        if self.resource_type != 'image':
            return None

        # Build url if we have upload response`
        return '%s%s/v%s/%s.jpg' % (self.base_url, s, self.version, self.public_id)
