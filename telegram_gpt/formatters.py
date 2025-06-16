class Formatters:
    @staticmethod
    def models_help():
        return (
            f"`/models usage\n\n`"
            f"`/models get`\n"
            f"`/models list`\n"
            f"`/models set model <str>`\n"
            f"`/models set temperature <float[0:2]>`\n"
            f"`/models set frequency <float[-2:2]>`\n"
            f"`/models set presence <float[-2:2]>`\n"
            f"`/models set top <float[0:1]>`\n"
        )