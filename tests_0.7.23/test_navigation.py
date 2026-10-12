import importlib.util
from pathlib import Path
import sys
import types
import unittest
from unittest.mock import Mock

class NavigationTests(unittest.TestCase):
    def load(self, current=10000, folder='videodb://tvshows/titles/1/1/'):
        xbmc=types.ModuleType('xbmc'); gui=types.ModuleType('xbmcgui')
        gui.getCurrentWindowId=Mock(return_value=current)
        xbmc.getCondVisibility=Mock(return_value=False)
        labels={'Container.FolderPath':folder,'Container(50).NumItems':'2',
                'Container(50).ListItemAbsolute(0).DBID':'7',
                'Container(50).ListItemAbsolute(0).DBTYPE':'episode',
                'Container(50).ListItemAbsolute(1).DBID':'8',
                'Container(50).ListItemAbsolute(1).DBTYPE':'episode'}
        xbmc.getInfoLabel=lambda key:labels.get(key,'')
        def builtin(command):
            if command.startswith('ActivateWindow'):gui.getCurrentWindowId.return_value=10025
        xbmc.executebuiltin=Mock(side_effect=builtin)
        sys.modules['xbmc']=xbmc;sys.modules['xbmcgui']=gui
        spec=importlib.util.spec_from_file_location('navigation_test',Path(__file__).resolve().parents[1]/'addon_0.7.23/return_navigation.py')
        module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
        return module,xbmc
    def test_return_from_home_and_focus_same_or_next_episode(self):
        for watched,index in [(False,0),(True,1)]:
            module,xbmc=self.load()
            context={'window':10025,'control':50,'folder':'videodb://tvshows/titles/1/1/','kind':'episode','selected':'7','next':'8'}
            module.restore(context,watched,Mock(abortRequested=lambda:False,waitForAbort=lambda _:False))
            self.assertEqual(xbmc.executebuiltin.call_count,2)
            self.assertEqual(xbmc.executebuiltin.call_args.args[0],f'SetFocus(50,{index},absolute)')
    def test_do_not_interrupt_other_folder(self):
        module,xbmc=self.load(10025,'videodb://movies/titles/')
        module.restore({'window':10025,'folder':'videodb://tvshows/titles/1/1/'},False,Mock(waitForAbort=lambda _:False))
        xbmc.executebuiltin.assert_not_called()
    def test_old_session_has_no_navigation(self):
        module,xbmc=self.load()
        module.restore(None,False,Mock())
        xbmc.executebuiltin.assert_not_called()

    def test_early_return_opens_folder_without_selecting_item(self):
        module, xbmc = self.load()
        context = {'window':10025, 'folder':'videodb://tvshows/titles/1/1/'}
        self.assertTrue(module.open_folder(context, Mock(waitForAbort=lambda _:False)))
        self.assertEqual(xbmc.executebuiltin.call_count, 1)
        self.assertTrue(xbmc.executebuiltin.call_args.args[0].startswith('ActivateWindow'))
