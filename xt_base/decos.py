import functools

from dtlib.tornado.utils import save_api_counts


def get_callback_result(callback, res_str):
    """
    根据callback后的jsonp语句
    :param callback:
    :param res_str:
    :return:
    """
    if callback is None:
        return res_str
    else:
        return '%s(%s)' % (callback.encode("utf-8"), res_str)



def user_get_api_counts(method):
    """
    获取api调用的次数,用于做用户的行为统计分析,后面还有利用组织的分析的。但是这个可能需要storm做实时统计了。
    :param method:
    :return:
    """

    @functools.wraps(method)
    async def wrapper(self, *args, **kwargs):
        method(self, *args, **kwargs)
        await save_api_counts(self)

    return wrapper



