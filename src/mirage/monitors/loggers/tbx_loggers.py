# ---INFO-----------------------------------------------------------------------
"""
Module for logging tensorboardX activity.
"""

__all__ = [
    "TbxTimeseriesLoggerV1",
]

# ---DEPENDENCIES---------------------------------------------------------------
import typing as tp
import socket
import tensorboard as tb
import tensorboardX as tbx

if tp.TYPE_CHECKING:
    from ...engines import EngineV1


# ---TbxTimeseriesLogger--------------------------------------------------------
class TbxTimeseriesLoggerV1(tbx.SummaryWriter):
    """
    TensorboardX logger for EngineV1 type.

    Parameters
    ----------
    engine : EngineV1
        Engine object to log.
    ldr : str
        Directory to save logs.
    env : str
        Environment to run tensorboard server. Must be 'colab' or 'local'.
    """

    def __init__(self, engine: "EngineV1", ldr: str, env: str, **kwargs):
        super(TbxTimeseriesLoggerV1, self).__init__(
            ldr, 
            max_queue=3, 
            flush_secs=10, 
            **kwargs,
        )
        self.engine = engine
        self.engine.O.append(self)
        self.ldr = ldr
        self.env = env
        if self.env not in ["colab", "local"]:
            raise ValueError(f"env. must be 'colab' or 'local'")
        self.regobj = {}

    def start_server(self):
        """
        Start tensorboard server.
        """
        if self.env == "colab":
            tb.notebook.start("--logdir", self.ldr)
        elif self.env == "local":
            tboard = tb.program.TensorBoard()
            tboard.configure(argv=[None, "--logdir", self.ldr, "--bind_all"])
            self.lurl = tboard.launch()
            # get port from lurl
            lurl_port = self.lurl.split(":")[-1]
            nip = socket.gethostbyname(socket.gethostname())
            self.nurl = f"http://{nip}:{lurl_port}"
            self.engine.L.info(f" 📈 Tensorboard URL: {self.lurl} {self.nurl}")

    def register_objects(
        self,
        attribute_objects: tp.Dict[
            str, tp.Tuple[str, tp.Any | tp.List[tp.Tuple[tp.Any, str]]]
        ],
    ):
        """
        Register objects for logging.

        Parameters
        ----------
        attribute_objects : Dict[str, Tuple[str, Any | List[Tuple[Any, str]]]]
        """
        # Loop through the attribute_objects dictionary and only register the
        # objects that are not already registered.
        for plot_name, (attr, objs) in attribute_objects.items():
            if plot_name not in self.regobj:
                self.regobj[plot_name] = (attr, objs)
            else:
                self.engine.L.warning(f" ⚠️ {plot_name} is already registered.")

    def observe(self):
        """
        Observe the engine and log the data for 1 step.
        """
        if self.regobj is not None:
            for plot_name, (attr, objs) in self.regobj.items():
                if isinstance(objs, list):
                    scalar_group = {o[1]: getattr(o[0], attr) for o in objs}
                    self.add_scalars(
                        plot_name,
                        scalar_group,
                        self.engine.STEP,
                    )
                else:
                    self.add_scalar(
                        plot_name,
                        getattr(objs, attr),
                        self.engine.STEP,
                    )

        current_keys = [
            key
            for key in self.engine.info_history
            if key.endswith(f"/{self.engine.STEP}")
        ]
        for key in current_keys:
            for attr, value in self.engine.info_history[key].items():
                self.add_scalar(
                    f"{key.split('/')[0]}/{attr}", 
                    value, 
                    self.engine.STEP,
                )

        run_h = self.engine.run_call_history
        if len(run_h) > 1:
            time_diff = [
                next_time - current_time
                for current_time, next_time in zip(run_h, run_h[1:])
            ]
            self.add_scalar(
                "average_duration_between_runs",
                sum(time_diff) / len(time_diff),
                self.engine.STEP,
            )
