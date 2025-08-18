import asyncio
import datetime
import itertools
import logging
from collections.abc import Awaitable, Callable, Coroutine, Generator, Iterable, Sized
from typing import Any
from requests import Response
from requests.auth import HTTPBasicAuth
from . import (
    GET,
    POST,
    LOCATION,
    RETRY_AFTER,
    EQUITY,
    Null,
    Alpha,
    MultiAlpha,
    Region,
    Delay,
    Universe,
    InstrumentType,
    DataCategory,
    FieldType,
    DatasetsOrder,
    FieldsOrder,
    Status,
    AlphaType,
    AlphaCategory,
    Language,
    Color,
    Neutralization,
    UnitHandling,
    NanHandling,
    Pasteurization,
    AlphasOrder,
)
from .auto_auth_session import AutoAuthSession
from .filter_range import FilterRange
from .wqb_urls import (
    URL_ALPHAS_ALPHAID,
    URL_ALPHAS_ALPHAID_CHECK,
    URL_ALPHAS_ALPHAID_SUBMIT,
    URL_AUTHENTICATION,
    URL_DATAFIELDS,
    URL_DATAFIELDS_FIELDID,
    URL_DATASETS,
    URL_DATASETS_DATASETID,
    URL_OPERATORS,
    URL_SIMULATIONS,
    URL_USERS_SELF_ALPHAS,
)

__all__ = ['print', 'wqb_logger', 'to_multi_alphas', 'concurrent_await', 'WQBSession']


_print = print


def print(
    *args,
    **kwargs,
) -> None:
    """
    Prints, and then flushes instantly.

    The usage is the same as the built-in `print`.

    Parameters
    ----------
    See also the built-in `print`.

    Returns
    -------
    None

    Notes
    -----
    `args` and `kwargs` are passed to the built-in `print`. `flush` is
    overridden to True no matter what.
    """
    kwargs['flush'] = True
    _print(*args, **kwargs)


def wqb_logger(
    *,
    name: str | None = None,
) -> logging.Logger:
    """
    Returns a pre-configured `logging.Logger` object.

    INFO logs are written to both the .log file and the console.

    WARNING logs are written to the console only.

    Parameters
    ----------
    name: str | None = None
        `logging.Logger.name`. If *None*, it is set to 'wqb' followed by
        the current datetime. The filename of the .log file is set to
        `name` followed by '.log'.

    Returns
    -------
    logging.Logger
        A pre-configured `logging.Logger` object.
    """
    if name is None:
        name = 'wqb' + datetime.datetime.now().strftime('%Y%m%d%H%M%S')
    logger = logging.getLogger(name=name)
    logger.setLevel(logging.INFO)
    handler1 = logging.FileHandler(f"{logger.name}.log")
    handler1.setLevel(logging.INFO)
    handler1.setFormatter(
        logging.Formatter(fmt='# %(levelname)s %(asctime)s\n%(message)s\n')
    )
    logger.addHandler(handler1)
    handler2 = logging.StreamHandler()
    handler2.setLevel(logging.WARNING)
    handler2.setFormatter(
        logging.Formatter(fmt='# %(levelname)s %(asctime)s\n%(message)s\n')
    )
    logger.addHandler(handler2)
    return logger


def to_multi_alphas(
    alphas: Iterable[Alpha],
    multiple: int | Iterable[Any],
) -> Generator[MultiAlpha, None, None]:
    """
    Converts an iterable series of `Alpha` objects to an iterable series
    of `MultiAlpha` objects.

    Parameters
    ----------
    alphas: Iterable[Alpha]
        The iterable series of `Alpha` objects.
    multiple: int | Iterable[Any]
        The number of `Alpha` objects to be grouped into a `MultiAlpha`
        object. If *int*, the `Alpha` objects are grouped by it. If
        *Iterable[Any]*, the `Alpha` objects are grouped by its length.

    Returns
    -------
    Iterable[MultiAlpha]
        An iterable series of `MultiAlpha` objects.

    Examples
    --------
    >>> alphas = [{...} for _ in range(6)]
    >>> alphas
    [{...}, {...}, {...}, {...}, {...}, {...}]
    >>> multi_alphas = list(wqb.to_multi_alphas(alphas, 3))
    >>> multi_alphas
    [[{...}, {...}, {...}], [{...}, {...}, {...}]]
    """
    alphas = iter(alphas)
    multiple = range(multiple) if isinstance(multiple, int) else tuple(multiple)
    try:
        while True:
            multi_alpha = []
            for _ in multiple:
                multi_alpha.append(next(alphas))
            yield multi_alpha
    except StopIteration as e:
        if 0 < len(multi_alpha):
            yield multi_alpha


async def concurrent_await(
    awaitables: Iterable[Awaitable[Any]],
    *,
    concurrency: int | asyncio.Semaphore | None = None,
    return_exceptions: bool = False,
) -> Coroutine[None, None, list[Any | BaseException]]:
    """
    Returns a `Coroutine` object that awaits an iterable series of
    `Awaitable` objects with a concurrency limit that controls the
    maximum number of `Awaitable` objects that can be awaited at the
    same time.

    Parameters
    ----------
    awaitables: Iterable[Awaitable[Any]]
        The iterable series of `Awaitable` objects.
    concurrency: int | asyncio.Semaphore | None = None
        The maximum number of `Awaitable` objects that can be awaited at
        the same time. If *int | asyncio.Semaphore*, the concurrency
        limit is set to it. If *None*, there is no concurrency limit.
    return_exceptions: bool = False
        Whether to return exceptions instead of raising them.

    Returns
    -------
    Coroutine[None, None, list[Any | BaseException]]
        A `Coroutine` object that awaits `Awaitable` objects
        concurrently.
    """
    if concurrency is None:
        return await asyncio.gather(*awaitables)
    if isinstance(concurrency, int):
        concurrency = asyncio.Semaphore(value=concurrency)

    async def semaphore_wrapper(
        awaitable: Awaitable[Any],
    ) -> Coroutine[None, None, Any]:
        """
        Wraps an `Awaitable` object with `concurrency`.

        Parameters
        ----------
        awaitable: Awaitable[Any]
            The `Awaitable` object to be wrapped.

        Returns
        -------
        Coroutine[None, None, Any]
            A `Coroutine` object that awaits the wrapped `Awaitable`
            object.
        """
        async with concurrency:
            result = await awaitable
        return result

    return await asyncio.gather(
        *(semaphore_wrapper(awaitable) for awaitable in awaitables),
        return_exceptions=return_exceptions,
    )


class WQBSession(AutoAuthSession):
    """
    A class that implements common APIs of WorldQuant BRAIN platform.
    """

    def __init__(
        self,
        wqb_auth: tuple[str, str] | HTTPBasicAuth,
        *,
        logger: logging.Logger = logging.root,
        **kwargs,
    ) -> None:
        """
        Initializes a `WQBSession` object.

        Parameters
        ----------
        wqb_auth: tuple[str, str] | HTTPBasicAuth
            The authentication credentials that consist of email and
            password.
        logger: logging.Logger = logging.root
            The `logging.Logger` object to log requests.

        Returns
        -------
        None

        Notes
        -----
        No `args` are accepted, while `kwargs` are passed to
        `AutoAuthSession.__init__`.

        Examples
        --------
        Without setting `logger`:

        >>> wqbs = wqb.WQBSession(('<email>', '<password>'))

        With setting `logger` (Recommended):

        >>> logger = wqb.wqb_logger()
        >>> wqbs = wqb.WQBSession(
        ...     ('<email>', '<password>'),
        ...     logger=logger,
        ... )
        """
        if not isinstance(wqb_auth, HTTPBasicAuth):
            wqb_auth = HTTPBasicAuth(*wqb_auth)
        kwargs['auth'] = wqb_auth
        super().__init__(
            POST,
            URL_AUTHENTICATION,
            auth_expected=lambda resp: 201 == resp.status_code,
            expected=lambda resp: resp.status_code not in (204, 401, 429),
            logger=logger,
            **kwargs,
        )
        self.expected_location = (
            lambda resp: self.expected(resp) and LOCATION in resp.headers
        )

    def __repr__(
        self,
    ) -> str:
        """
        Returns a string representation of the `WQBSession` object.

        Returns
        -------
        str
            A string representation of the `WQBSession` object.
        """
        return f"<WQBSession [{repr(self.wqb_auth.username)}]>"

    @property
    def wqb_auth(
        self,
    ) -> HTTPBasicAuth:
        """
        `wqb_auth`
        """
        return self.kwargs['auth']

    @wqb_auth.setter
    def wqb_auth(
        self,
        wqb_auth: tuple[str, str] | HTTPBasicAuth,
    ) -> None:
        """
        `wqb_auth`
        """
        if not isinstance(wqb_auth, HTTPBasicAuth):
            wqb_auth = HTTPBasicAuth(*wqb_auth)
        self.kwargs['auth'] = wqb_auth

    def get_authentication(
        self,
        *args,
        log: str | None = '',
        **kwargs,
    ) -> Response:
        """
        Sends a GET request to `URL_AUTHENTICATION`.

        Parameters
        ----------
        log: str | None = ''
            The message to be appended. If *None*, logging is disabled.

        Returns
        -------
        Response
            A `Response` object.

        Notes
        -----
        `args` and `kwargs` are passed to `Session.get`.

        Examples
        --------
        >>> wqbs = wqb.WQBSession(('<email>', '<password>'))
        >>> resp = wqbs.get_authentication()
        >>> resp.ok
        True
        """
        url = URL_AUTHENTICATION
        resp = self.get(url, *args, **kwargs)
        if log is not None:
            self.logger.info(
                '\n'.join(
                    (
                        f"{self}.get_authentication(...) [",
                        f"    {url}",
                        f"]: {log}",
                    )
                )
            )
        return resp

    def post_authentication(
        self,
        *args,
        log: str | None = '',
        **kwargs,
    ) -> Response:
        """
        Sends a POST request to `URL_AUTHENTICATION`.

        Parameters
        ----------
        log: str | None = ''
            The message to be appended. If *None*, logging is disabled.

        Returns
        -------
        Response
            A `Response` object.

        Notes
        -----
        `args` and `kwargs` are passed to `Session.post`.

        Examples
        --------
        >>> wqbs = wqb.WQBSession(('<email>', '<password>'))
        >>> resp = wqbs.post_authentication(auth=wqbs.wqb_auth)
        >>> resp.ok
        True
        """
        url = URL_AUTHENTICATION
        resp = self.post(url, *args, auth=self.wqb_auth, **kwargs)
        if log is not None:
            self.logger.info(
                '\n'.join(
                    (
                        f"{self}.post_authentication(...) [",
                        f"    {url}",
                        f"]: {log}",
                    )
                )
            )
        return resp

    def delete_authentication(
        self,
        *args,
        log: str | None = '',
        **kwargs,
    ) -> Response:
        """
        Sends a DELETE request to `URL_AUTHENTICATION`.

        Parameters
        ----------
        log: str | None = ''
            The message to be appended. If *None*, logging is disabled.

        Returns
        -------
        Response
            A `Response` object.

        Notes
        -----
        `args` and `kwargs` are passed to `Session.delete`.

        Examples
        --------
        >>> wqbs = wqb.WQBSession(('<email>', '<password>'))
        >>> resp = wqbs.delete_authentication()
        >>> resp.ok
        True
        """
        url = URL_AUTHENTICATION
        resp = self.delete(url, *args, **kwargs)
        if log is not None:
            self.logger.info(
                '\n'.join(
                    (
                        f"{self}.delete_authentication(...) [",
                        f"    {url}",
                        f"]: {log}",
                    )
                )
            )
        return resp

    def head_authentication(
        self,
        *args,
        log: str | None = '',
        **kwargs,
    ) -> Response:
        """
        Sends a HEAD request to `URL_AUTHENTICATION`.

        Parameters
        ----------
        log: str | None = ''
            The message to be appended. If *None*, logging is disabled.

        Returns
        -------
        Response
            A `Response` object.

        Notes
        -----
        `args` and `kwargs` are passed to `Session.head`.

        Examples
        --------
        >>> wqbs = wqb.WQBSession(('<email>', '<password>'))
        >>> resp = wqbs.head_authentication()
        >>> resp.ok
        True
        """
        url = URL_AUTHENTICATION
        resp = self.head(url, *args, **kwargs)
        if log is not None:
            self.logger.info(
                '\n'.join(
                    (
                        f"{self}.head_authentication(...) [",
                        f"    {url}",
                        f"]: {log}",
                    )
                )
            )
        return resp

    def search_operators(
        self,
        *args,
        log: str | None = '',
        **kwargs,
    ) -> Response:
        """
        Sends a GET request to `URL_OPERATORS`.

        Parameters
        ----------
        log: str | None = ''
            The message to be appended. If *None*, logging is disabled.

        Returns
        -------
        Response
            A `Response` object.

        Notes
        -----
        `args` and `kwargs` are passed to `Session.get`.

        Examples
        --------
        >>> wqbs = wqb.WQBSession(('<email>', '<password>'))
        >>> resp = wqbs.search_operators()
        >>> resp.ok
        True
        """
        url = URL_OPERATORS
        resp = self.get(url, *args, **kwargs)
        if log is not None:
            self.logger.info(
                '\n'.join(
                    (
                        f"{self}.search_operators(...) [",
                        f"    {url}",
                        f"]: {log}",
                    )
                )
            )
        return resp

    def locate_dataset(
        self,
        dataset_id: str,
        *args,
        log: str | None = '',
        **kwargs,
    ) -> Response:
        """
        Sends a GET request to
        `URL_DATASETS_DATASETID.format(dataset_id)`.

        Parameters
        ----------
        dataset_id: str
            The dataset ID.
        log: str | None = ''
            The message to be appended. If *None*, logging is disabled.

        Returns
        -------
        Response
            A `Response` object.

        Notes
        -----
        `args` and `kwargs` are passed to `Session.get`.

        Examples
        --------
        >>> wqbs = wqb.WQBSession(('<email>', '<password>'))
        >>> resp = wqbs.locate_dataset('pv1')
        >>> resp.ok
        True
        """
        url = URL_DATASETS_DATASETID.format(dataset_id)
        resp = self.get(url, *args, **kwargs)
        if log is not None:
            self.logger.info(
                '\n'.join(
                    (
                        f"{self}.locate_dataset(...) [",
                        f"    {url}",
                        f"]: {log}",
                    )
                )
            )
        return resp

    def search_datasets_limited(
        self,
        region: Region,
        delay: Delay,
        universe: Universe,
        *args,
        instrument_type: InstrumentType = EQUITY,
        search: str | None = None,
        category: DataCategory | None = None,
        theme: bool | None = None,
        coverage: FilterRange | None = None,
        value_score: FilterRange | None = None,
        alpha_count: FilterRange | None = None,
        user_count: FilterRange | None = None,
        order: DatasetsOrder | None = None,
        limit: int = 50,
        offset: int = 0,
        others: Iterable[str] | None = None,
        log: str | None = '',
        **kwargs,
    ) -> Response:
        limit = min(max(limit, 1), 50)
        offset = min(max(offset, 0), 10000 - limit)
        params = [
            f"region={region}",
            f"delay={delay}",
            f"universe={universe}",
        ]
        params.append(f"instrumentType={instrument_type}")
        if search is not None:
            params.append(f"search={search}")
        if category is not None:
            params.append(f"category={category}")
        if theme is not None:
            params.append(f"theme={'true' if theme else 'false'}")
        if coverage is not None:
            params.append(coverage.to_params('coverage'))
        if value_score is not None:
            params.append(value_score.to_params('valueScore'))
        if alpha_count is not None:
            params.append(alpha_count.to_params('alphaCount'))
        if user_count is not None:
            params.append(user_count.to_params('userCount'))
        if order is not None:
            params.append(f"order={order}")
        params.append(f"limit={limit}")
        params.append(f"offset={offset}")
        if others is not None:
            params.extend(others)
        url = URL_DATASETS + '?' + '&'.join(params)
        resp = self.get(url, *args, **kwargs)
        if log is not None:
            self.logger.info(
                '\n'.join(
                    (
                        f"{self}.search_datasets_limited(...) [",
                        f"    {url}",
                        f"]: {log}",
                    )
                )
            )
        return resp

    def search_datasets(
        self,
        region: Region,
        delay: Delay,
        universe: Universe,
        *args,
        limit: int = 50,
        offset: int = 0,
        log: str | None = '',
        log_gap: int = 100,
        **kwargs,
    ) -> Generator[Response, None, None]:
        if log is None:
            log_gap = 0
        count = self.search_datasets_limited(
            region, delay, universe, *args, limit=1, offset=offset, log=log, **kwargs
        ).json()['count']
        offsets = range(offset, count, limit)
        if log is not None:
            self.logger.info(f"{self}.search_datasets(...) [start {offsets}]: {log}")
        total = len(offsets)
        for idx, offset in enumerate(offsets, start=1):
            yield self.search_datasets_limited(
                region,
                delay,
                universe,
                *args,
                limit=limit,
                offset=offset,
                log=(
                    f"{idx}/{total} = {int(100*idx/total)}%"
                    if 0 != log_gap and 0 == idx % log_gap
                    else None
                ),
                **kwargs,
            )
        if log is not None:
            self.logger.info(f"{self}.search_datasets(...) [finish {offsets}]: {log}")

    def locate_field(
        self,
        field_id: str,
        *args,
        log: str | None = '',
        **kwargs,
    ) -> Response:
        url = URL_DATAFIELDS_FIELDID.format(field_id)
        resp = self.get(url, *args, **kwargs)
        if log is not None:
            self.logger.info(
                '\n'.join(
                    (
                        f"{self}.locate_field(...) [",
                        f"    {url}",
                        f"]: {log}",
                    )
                )
            )
        return resp

    def search_fields_limited(
        self,
        region: Region,
        delay: Delay,
        universe: Universe,
        *args,
        instrument_type: InstrumentType = EQUITY,
        dataset_id: str | None = None,
        search: str | None = None,
        category: DataCategory | None = None,
        theme: bool | None = None,
        coverage: FilterRange | None = None,
        type: FieldType | None = None,
        alpha_count: FilterRange | None = None,
        user_count: FilterRange | None = None,
        order: FieldsOrder | None = None,
        limit: int = 50,
        offset: int = 0,
        others: Iterable[str] | None = None,
        log: str | None = '',
        **kwargs,
    ) -> Response:
        limit = min(max(limit, 1), 50)
        offset = min(max(offset, 0), 10000 - limit)
        params = [
            f"region={region}",
            f"delay={delay}",
            f"universe={universe}",
        ]
        params.append(f"instrumentType={instrument_type}")
        if dataset_id is not None:
            params.append(f"dataset.id={dataset_id}")
        if search is not None:
            params.append(f"search={search}")
        if category is not None:
            params.append(f"category={category}")
        if theme is not None:
            params.append(f"theme={'true' if theme else 'false'}")
        if coverage is not None:
            params.append(coverage.to_params('coverage'))
        if type is not None:
            params.append(f"type={type}")
        if alpha_count is not None:
            params.append(alpha_count.to_params('alphaCount'))
        if user_count is not None:
            params.append(user_count.to_params('userCount'))
        if order is not None:
            params.append(f"order={order}")
        params.append(f"limit={limit}")
        params.append(f"offset={offset}")
        if others is not None:
            params.extend(others)
        url = URL_DATAFIELDS + '?' + '&'.join(params)
        resp = self.get(url, *args, **kwargs)
        if log is not None:
            self.logger.info(
                '\n'.join(
                    (
                        f"{self}.search_fields_limited(...) [",
                        f"    {url}",
                        f"]: {log}",
                    )
                )
            )
        return resp

    def search_fields(
        self,
        region: Region,
        delay: Delay,
        universe: Universe,
        *args,
        limit: int = 50,
        offset: int = 0,
        log: str | None = '',
        log_gap: int = 100,
        **kwargs,
    ) -> Generator[Response, None, None]:
        if log is None:
            log_gap = 0
        count = self.search_fields_limited(
            region, delay, universe, *args, limit=1, offset=offset, log=log, **kwargs
        ).json()['count']
        offsets = range(offset, count, limit)
        if log is not None:
            self.logger.info(f"{self}.search_fields(...) [start {offsets}]: {log}")
        total = len(offsets)
        for idx, offset in enumerate(offsets, start=1):
            yield self.search_fields_limited(
                region,
                delay,
                universe,
                *args,
                limit=limit,
                offset=offset,
                log=(
                    f"{idx}/{total} = {int(100*idx/total)}%"
                    if 0 != log_gap and 0 == idx % log_gap
                    else None
                ),
                **kwargs,
            )
        if log is not None:
            self.logger.info(f"{self}.search_fields(...) [finish {offsets}]: {log}")

    def locate_alpha(
        self,
        alpha_id: str,
        *args,
        log: str | None = '',
        **kwargs,
    ) -> Response:
        url = URL_ALPHAS_ALPHAID.format(alpha_id)
        resp = self.get(url, *args, **kwargs)
        if log is not None:
            self.logger.info(
                '\n'.join(
                    (
                        f"{self}.locate_alpha(...) [",
                        f"    {url}",
                        f"]: {log}",
                    )
                )
            )
        return resp

    def filter_alphas_limited(
        self,
        *args,
        name: str | None = None,
        competition: bool | None = None,
        type: AlphaType | None = None,
        language: Language | None = None,
        date_created: FilterRange | None = None,
        favorite: bool | None = None,
        date_submitted: FilterRange | None = None,
        start_date: FilterRange | None = None,
        status: Status | None = None,
        category: AlphaCategory | None = None,
        color: Color | None = None,
        tag: str | None = None,
        hidden: bool | None = None,
        region: Region | None = None,
        instrument_type: InstrumentType | None = None,
        universe: Universe | None = None,
        delay: Delay | None = None,
        decay: FilterRange | None = None,
        neutralization: Neutralization | None = None,
        truncation: FilterRange | None = None,
        unit_handling: UnitHandling | None = None,
        nan_handling: NanHandling | None = None,
        pasteurization: Pasteurization | None = None,
        sharpe: FilterRange | None = None,
        returns: FilterRange | None = None,
        pnl: FilterRange | None = None,
        turnover: FilterRange | None = None,
        drawdown: FilterRange | None = None,
        margin: FilterRange | None = None,
        fitness: FilterRange | None = None,
        book_size: FilterRange | None = None,
        long_count: FilterRange | None = None,
        short_count: FilterRange | None = None,
        sharpe60: FilterRange | None = None,
        sharpe125: FilterRange | None = None,
        sharpe250: FilterRange | None = None,
        sharpe500: FilterRange | None = None,
        os_is_sharpe_ratio: FilterRange | None = None,
        pre_close_sharpe: FilterRange | None = None,
        pre_close_sharpe_ratio: FilterRange | None = None,
        self_correlation: FilterRange | None = None,
        prod_correlation: FilterRange | None = None,
        order: AlphasOrder | None = None,
        limit: int = 100,
        offset: int = 0,
        others: Iterable[str] | None = None,
        log: str | None = '',
        **kwargs,
    ) -> Response:
        limit = min(max(limit, 1), 100)
        offset = min(max(offset, 0), 10000 - limit)
        params = []
        if name is not None:
            params.append(f"name{name if name[0] in '~=' else '~' + name}")
        if competition is not None:
            params.append(f"competition={'true' if competition else 'false'}")
        if type is not None:
            params.append(f"type={type}")
        if language is not None:
            params.append(f"settings.language={language}")
        if date_created is not None:
            params.append(date_created.to_params('dateCreated'))
        if favorite is not None:
            params.append(f"favorite={'true' if favorite else 'false'}")
        if date_submitted is not None:
            params.append(date_submitted.to_params('dateSubmitted'))
        if start_date is not None:
            params.append(start_date.to_params('os.startDate'))
        if status is not None:
            params.append(f"status={status}")
        if category is not None:
            params.append(f"category={category}")
        if color is not None:
            params.append(f"color={color}")
        if tag is not None:
            params.append(f"tag={tag}")
        if hidden is not None:
            params.append(f"hidden={'true' if hidden else 'false'}")
        if region is not None:
            params.append(f"settings.region={region}")
        if instrument_type is not None:
            params.append(f"settings.instrumentType={instrument_type}")
        if universe is not None:
            params.append(f"settings.universe={universe}")
        if delay is not None:
            params.append(f"settings.delay={delay}")
        if decay is not None:
            params.append(decay.to_params('settings.decay'))
        if neutralization is not None:
            params.append(f"settings.neutralization={neutralization}")
        if truncation is not None:
            params.append(truncation.to_params('settings.truncation'))
        if unit_handling is not None:
            params.append(f"settings.unitHandling={unit_handling}")
        if nan_handling is not None:
            params.append(f"settings.nanHandling={nan_handling}")
        if pasteurization is not None:
            params.append(f"settings.pasteurization={pasteurization}")
        if sharpe is not None:
            params.append(sharpe.to_params('is.sharpe'))
        if returns is not None:
            params.append(returns.to_params('is.returns'))
        if pnl is not None:
            params.append(pnl.to_params('is.pnl'))
        if turnover is not None:
            params.append(turnover.to_params('is.turnover'))
        if drawdown is not None:
            params.append(drawdown.to_params('is.drawdown'))
        if margin is not None:
            params.append(margin.to_params('is.margin'))
        if fitness is not None:
            params.append(fitness.to_params('is.fitness'))
        if book_size is not None:
            params.append(book_size.to_params('is.bookSize'))
        if long_count is not None:
            params.append(long_count.to_params('is.longCount'))
        if short_count is not None:
            params.append(short_count.to_params('is.shortCount'))
        if sharpe60 is not None:
            params.append(sharpe60.to_params('os.sharpe60'))
        if sharpe125 is not None:
            params.append(sharpe125.to_params('os.sharpe125'))
        if sharpe250 is not None:
            params.append(sharpe250.to_params('os.sharpe250'))
        if sharpe500 is not None:
            params.append(sharpe500.to_params('os.sharpe500'))
        if os_is_sharpe_ratio is not None:
            params.append(os_is_sharpe_ratio.to_params('os.osISSharpeRatio'))
        if pre_close_sharpe is not None:
            params.append(pre_close_sharpe.to_params('os.preCloseSharpe'))
        if pre_close_sharpe_ratio is not None:
            params.append(pre_close_sharpe_ratio.to_params('os.preCloseSharpeRatio'))
        if self_correlation is not None:
            params.append(self_correlation.to_params('is.selfCorrelation'))
        if prod_correlation is not None:
            params.append(prod_correlation.to_params('is.prodCorrelation'))
        if order is not None:
            params.append(f"order={order}")
        params.append(f"limit={limit}")
        params.append(f"offset={offset}")
        if others is not None:
            params.extend(others)
        url = URL_USERS_SELF_ALPHAS + '?' + '&'.join(params)
        url = url.replace('+', '%2B')  # TODO: Can be improved.
        resp = self.get(url, *args, **kwargs)
        if log is not None:
            self.logger.info(
                '\n'.join(
                    (
                        f"{self}.filter_alphas_limited(...) [",
                        f"    {url}",
                        f"]: {log}",
                    )
                )
            )
        return resp

    def filter_alphas(
        self,
        *args,
        limit: int = 100,
        offset: int = 0,
        log: str | None = '',
        log_gap: int = 100,
        **kwargs,
    ) -> Generator[Response, None, None]:
        if log is None:
            log_gap = 0
        count = self.filter_alphas_limited(
            *args, limit=1, offset=offset, log=log, **kwargs
        ).json()['count']
        offsets = range(offset, count, limit)
        if log is not None:
            self.logger.info(f"{self}.filter_alphas(...) [start {offsets}]: {log}")
        total = len(offsets)
        for idx, offset in enumerate(offsets, start=1):
            yield self.filter_alphas_limited(
                *args,
                limit=limit,
                offset=offset,
                log=(
                    f"{idx}/{total} = {int(100*idx/total)}%"
                    if 0 != log_gap and 0 == idx % log_gap
                    else None
                ),
                **kwargs,
            )
        if log is not None:
            self.logger.info(f"{self}.filter_alphas(...) [finish {offsets}]: {log}")

    def patch_properties(
        self,
        alpha_id: str,
        *args,
        favorite: bool | None = None,
        hidden: bool | None = None,
        name: str | Null | None = None,
        category: AlphaCategory | Null | None = None,
        tags: str | Iterable[str] | Null | None = None,
        color: Color | Null | None = None,
        regular_description: str | Null | None = None,
        log: str | None = '',
        **kwargs,
    ) -> Response:
        url = URL_ALPHAS_ALPHAID.format(alpha_id)
        properties = {}
        if favorite is not None:
            properties['favorite'] = favorite
        if hidden is not None:
            properties['hidden'] = hidden
        if name is not None:
            properties['name'] = None if isinstance(name, Null) else name
        if category is not None:
            properties['category'] = None if isinstance(category, Null) else category
        if tags is not None:
            properties['tags'] = (
                []
                if isinstance(tags, Null)
                else [tags] if isinstance(tags, str) else list(tags)
            )
        if color is not None:
            properties['color'] = None if isinstance(color, Null) else color
        if regular_description is not None:
            properties['regular'] = {}
            properties['regular']['description'] = (
                None if isinstance(regular_description, Null) else regular_description
            )
        resp = self.patch(url, json=properties, *args, **kwargs)
        if log is not None:
            self.logger.info(
                '\n'.join(
                    (
                        f"{self}.patch_properties(...) [",
                        f"    {url}",
                        f"    {properties}",
                        f"]: {log}",
                    )
                )
            )
        return resp

    async def retry(
        self,
        method: str,
        url: str,
        *args,
        max_tries: int | Iterable[Any] = itertools.repeat(None),
        max_key_errors: int = 1,
        max_value_errors: int = 1,
        delay_key_error: float = 2.0,
        delay_value_error: float = 2.0,
        on_start: Callable[[dict[str, Any]], None] | None = None,
        on_finish: Callable[[dict[str, Any]], None] | None = None,
        on_success: Callable[[dict[str, Any]], None] | None = None,
        on_failure: Callable[[dict[str, Any]], None] | None = None,
        log: str | None = '',
        **kwargs,
    ) -> Coroutine[None, None, Response | None]:
        if isinstance(max_tries, int):
            max_tries = range(max_tries)
        tries = 0
        resp = None
        key_errors = 0
        value_errors = 0
        if log is not None:
            self.logger.info(f"{self}.retry(...) [start {max_tries}]: {log}")
        if on_start is not None:
            on_start(locals())
        for tries, _ in enumerate(max_tries, start=1):
            resp = self.request(method, url, *args, **kwargs)
            try:
                await asyncio.sleep(float(resp.headers[RETRY_AFTER]))
            except KeyError as e:
                key_errors += 1
                if max_key_errors <= key_errors:
                    if log is not None:
                        self.logger.info(
                            f"{self}.retry(...) [{key_errors} key_errors]: {log}"
                        )
                    if on_success is not None:
                        on_success(locals())
                    break
                await asyncio.sleep(delay_key_error)
            except ValueError as e:
                value_errors += 1
                if max_value_errors <= value_errors:
                    if log is not None:
                        self.logger.info(
                            f"{self}.retry(...) [{value_errors} value_errors]: {log}"
                        )
                    if on_success is not None:
                        on_success(locals())
                    break
                await asyncio.sleep(delay_value_error)
        else:
            self.logger.warning(
                '\n'.join(
                    (
                        f"{self}.retry(...) [max {tries} tries ran out]",
                        f"self.request(method, url, *args, **kwargs):",
                        f"    method: {method}",
                        f"    url: {url}",
                        f"    args: {args}",
                        f"    kwargs: {kwargs}",
                        f"{resp}:",
                        f"    status_code: {resp.status_code}",
                        f"    reason: {resp.reason}",
                        f"    url: {resp.url}",
                        f"    elapsed: {resp.elapsed}",
                        f"    headers: {resp.headers}",
                        f"    text: {resp.text}",
                    )
                )
            )
            if on_failure is not None:
                on_failure(locals())
        if log is not None:
            self.logger.info(f"{self}.retry(...) [finish {tries} tries]: {log}")
        if on_finish is not None:
            on_finish(locals())
        return resp

    async def simulate(
        self,
        target: Alpha | MultiAlpha,
        *args,
        max_tries: int | Iterable[Any] = range(600),
        on_nolocation: Callable[[dict[str, Any]], None] | None = None,
        log: str | None = '',
        retry_log: str | None = None,
        **kwargs,
    ) -> Coroutine[None, None, Response | None]:
        resp = self.post(
            URL_SIMULATIONS,
            json=target,
            expected=self.expected_location,
            max_tries=60,
            delay_unexpected=5.0,
        )
        try:
            url = resp.headers[LOCATION]
        except KeyError as e:
            self.logger.warning(
                '\n'.join(
                    (
                        f"{self}.simulate(...) [",
                        f"    {repr(e)}",
                        f"    {target}",
                        f"]:",
                        f"{resp}:",
                        f"    status_code: {resp.status_code}",
                        f"    reason: {resp.reason}",
                        f"    url: {resp.url}",
                        f"    elapsed: {resp.elapsed}",
                        f"    headers: {resp.headers}",
                        f"    text: {resp.text}",
                    )
                )
            )
            if on_nolocation is not None:
                on_nolocation(locals())
            return None
        resp = await self.retry(
            GET, url, *args, max_tries=max_tries, log=retry_log, **kwargs
        )
        if log is not None:
            self.logger.info(
                '\n'.join(
                    (
                        f"{self}.simulate(...) [",
                        f"    {url}",
                        # f"    {target}",
                        f"]: {log}",
                    )
                )
            )
        return resp

    async def concurrent_simulate(
        self,
        targets: Iterable[Alpha | MultiAlpha],
        concurrency: int | asyncio.Semaphore,
        *args,
        return_exceptions: bool = False,
        log: str | None = '',
        log_gap: int = 100,
        **kwargs,
    ) -> Coroutine[None, None, list[Response | BaseException]]:
        if not isinstance(targets, Sized):
            targets = list(targets)
        if log is None:
            log_gap = 0
        if isinstance(concurrency, int):
            concurrency = asyncio.Semaphore(value=concurrency)
        total = len(targets)
        if log is not None:
            self.logger.info(
                f"{self}.concurrent_simulate(...) [start {total}, {concurrency._value}]: {log}"
            )
        resp = await concurrent_await(
            (
                self.simulate(
                    target,
                    *args,
                    log=(
                        f"{idx}/{total} = {int(100*idx/total)}%"
                        if 0 != log_gap and 0 == idx % log_gap
                        else None
                    ),
                    **kwargs,
                )
                for idx, target in enumerate(targets, start=1)
            ),
            concurrency=concurrency,
            return_exceptions=return_exceptions,
        )
        if log is not None:
            self.logger.info(
                f"{self}.concurrent_simulate(...) [finish {total}, {concurrency._value}]: {log}"
            )
        return resp

    async def check(
        self,
        alpha_id: str,
        *args,
        max_tries: int | Iterable[Any] = range(600),
        log: str | None = '',
        retry_log: str | None = None,
        **kwargs,
    ) -> Coroutine[None, None, Response | None]:
        url = URL_ALPHAS_ALPHAID_CHECK.format(alpha_id)
        resp = await self.retry(
            GET, url, *args, max_tries=max_tries, log=retry_log, **kwargs
        )
        if log is not None:
            self.logger.info(
                '\n'.join(
                    (
                        f"{self}.check(...) [",
                        f"    {url}",
                        f"]: {log}",
                    )
                )
            )
        return resp

    async def concurrent_check(
        self,
        alpha_ids: Iterable[str],
        concurrency: int | asyncio.Semaphore,
        *args,
        return_exceptions: bool = False,
        log: str | None = '',
        log_gap: int = 100,
        **kwargs,
    ) -> Coroutine[None, None, list[Response | BaseException]]:
        if not isinstance(alpha_ids, Sized):
            alpha_ids = list(alpha_ids)
        if log is None:
            log_gap = 0
        if isinstance(concurrency, int):
            concurrency = asyncio.Semaphore(value=concurrency)
        total = len(alpha_ids)
        if log is not None:
            self.logger.info(
                f"{self}.concurrent_check(...) [start {total}, {concurrency._value}]: {log}"
            )
        resp = await concurrent_await(
            (
                self.check(
                    alpha_id,
                    *args,
                    log=(
                        f"{idx}/{total} = {int(100*idx/total)}%"
                        if 0 != log_gap and 0 == idx % log_gap
                        else None
                    ),
                    **kwargs,
                )
                for idx, alpha_id in enumerate(alpha_ids, start=1)
            ),
            concurrency=concurrency,
            return_exceptions=return_exceptions,
        )
        if log is not None:
            self.logger.info(
                f"{self}.concurrent_check(...) [finish {total}, {concurrency._value}]: {log}"
            )
        return resp

    async def submit(
        self,
        alpha_id: str,
        *args,
        max_tries: int | Iterable[Any] = range(600),
        log: str | None = '',
        retry_log: str | None = None,
        **kwargs,
    ) -> Coroutine[None, None, Response | None]:
        url = URL_ALPHAS_ALPHAID_SUBMIT.format(alpha_id)
        resp = await self.retry(
            POST, url, *args, max_tries=max_tries, log=retry_log, **kwargs
        )
        if log is not None:
            self.logger.info(
                '\n'.join(
                    (
                        f"{self}.submit(...) [",
                        f"    {url}",
                        f"]: {log}",
                    )
                )
            )
        return resp
