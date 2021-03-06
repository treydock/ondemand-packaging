import os
from tito.release.main import YumRepoReleaser
from tito.builder.main import Builder, MockBuilder
from tito.common import create_builder, run_command, run_command_print, info_out

class SRPMBuilder(Builder):
    def __init__(self, name=None, tag=None, build_dir=None,
                 config=None, user_config=None,
                 args=None, **kwargs):

        # Mock builders need to use the packages normally configured builder
        # to get at a proper SRPM:
        self.normal_builder = create_builder(name, tag, config,
                build_dir, user_config, args, **kwargs)

        Builder.__init__(self, name=name, tag=tag,
                build_dir=build_dir, config=config,
                user_config=user_config,
                args=args, **kwargs)

    def srpm(self, dist=None):
        """
        Build a source RPM.
        MockBuilder will use an instance of the normal builder for a package
        internally just so we can generate a SRPM correctly before we pass it
        into mock.
        """
        self.normal_builder.srpm(dist)
        self.srpm_location = self.normal_builder.srpm_location
        self.artifacts.append(self.srpm_location)

    def rpm(self):
        pass

    def cleanup(self):
        if self.srpm_location:
            proj_root = os.path.join(os.path.dirname(os.path.abspath(__file__)), '../..')
            gpgpass = os.path.join(proj_root, '.gpgpass')
            if os.path.isfile(gpgpass):
                run_command_func = run_command if self.quiet else run_command_print
                info_out("Signing: %s" % self.srpm_location)
                run_command_func("%s/rpm-sign.exp %s %s" % (proj_root, gpgpass, self.srpm_location))
        super(SRPMBuilder, self).cleanup()

class MockSignBuilder(MockBuilder):
    def _build_in_mock(self):
        run_command_func = run_command if self.quiet else run_command_print
        if not self.speedup:
            print("Initializing mock...")
            run_command_func("mock %s -r %s --init" % (self.mock_cmd_args, self.mock_tag))
        else:
            print("Skipping mock --init due to speedup option.")

        #print("Installing deps in mock...")
        #run_command_func("mock %s -r %s %s" % (
        #    self.mock_cmd_args, self.mock_tag, self.srpm_location))
        print("Building RPMs in mock...")
        run_command_func('mock %s -r %s --rebuild %s' %
                (self.mock_cmd_args, self.mock_tag, self.srpm_location))
        mock_output_dir = os.path.join(self.rpmbuild_dir, "mockoutput")
        run_command_func("mock %s -r %s --copyout /builddir/build/RPMS/ %s" %
                (self.mock_cmd_args, self.mock_tag, mock_output_dir))

        # Copy everything mock wrote out to /tmp/tito:
        files = os.listdir(mock_output_dir)
        run_command_func("cp -v %s/*.rpm %s" %
                (mock_output_dir, self.rpmbuild_basedir))
        print
        info_out("Wrote:")
        for rpm in files:
            rpm_path = os.path.join(self.rpmbuild_basedir, rpm)
            print("  %s" % rpm_path)
            self.artifacts.append(rpm_path)
        print

    def cleanup(self):
        if self.artifacts:
            proj_root = os.path.join(os.path.dirname(os.path.abspath(__file__)), '../..')
            gpgpass = os.path.join(proj_root, '.gpgpass')
            if os.path.isfile(gpgpass):
                run_command_func = run_command if self.quiet else run_command_print
                for a in self.artifacts:
                    info_out("Signing: %s" % a)
                    run_command_func("%s/rpm-sign.exp %s %s" % (proj_root, gpgpass, a))
        super(MockSignBuilder, self).cleanup()

class YumRepoReleaserKeepOld(YumRepoReleaser):
    def __init__(self, name=None, tag=None, build_dir=None,
            config=None, user_config=None,
            target=None, releaser_config=None, no_cleanup=False,
            test=False, auto_accept=False, **kwargs):
        super(YumRepoReleaserKeepOld, self).__init__(name, tag, build_dir,
            config, user_config,
            target, releaser_config, no_cleanup,
            test, auto_accept, **kwargs)
        if self.releaser_config.has_option(self.target, "keepold"):
            self.keepold = self.releaser_config.getboolean(self.target, "keepold")
        else:
            self.keepold = False

    def prune_other_versions(self, temp_dir):
        if self.keepold:
            info_out("YumRepoReleaserKeepOld: skip prune_other_versions")
        else:
            info_out("YumRepoReleaserKeepOld: running prune_other_versions")
            super(YumRepoReleaserKeepOld, self).prune_other_versions(temp_dir)

