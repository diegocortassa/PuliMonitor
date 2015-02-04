import json
import logging
import subprocess

from PyQt4.QtCore import Qt
from PyQt4.QtGui import QWidget, QVBoxLayout, QHBoxLayout, QMessageBox, qApp
import requests

from pulimonitor.network.requesthandler import RequestHandler
from pulimonitor.ui.action import Action
from pulimonitor.ui.rendernode.model import RenderNodeTableProxyModel, RenderNodeTableModel
from pulimonitor.ui.rendernode.stats import RenderNodeStatsWidget
from pulimonitor.ui.rendernode.view import RenderNodeTableView
from pulimonitor.ui.searchlineedit import SearchLineEdit
from pulimonitor.util.config import Config
from pulimonitor.util.user import currentUser


class RenderNodePanel(QWidget):

    sourceModel = None

    def __init__(self, parent=None):
        super(RenderNodePanel, self).__init__(parent)
        self.log = logging.getLogger(__name__)
        self.mainLayout = QVBoxLayout(self)
        self.mainLayout.setSpacing(2)
        self.searchLineEdit = SearchLineEdit(self)
        searchLayout = QHBoxLayout()
        searchLayout.addWidget(self.searchLineEdit)
        self.tableView = RenderNodeTableView(self)
        self.statsWidget = RenderNodeStatsWidget(self)
        if RenderNodePanel.sourceModel is None:
            RenderNodePanel.sourceModel = RenderNodeTableModel(qApp)
        self.tableModel = RenderNodeTableProxyModel(RenderNodePanel.sourceModel, self)
        self.searchLineEdit.setModel(self.tableModel)
        self.tableView.setModel(self.tableModel)
        self.mainLayout.addLayout(searchLayout)
        self.mainLayout.addWidget(self.tableView)
        self.mainLayout.addWidget(self.statsWidget)
        self.setupActions()

    def onPauseAction(self):
        '''
        Slot called once the pause action is triggered
        '''
        rh = RequestHandler()
        for index in self.tableView.selectionModel().selectedRows():
            rn = index.data(Qt.UserRole)
            self.log.info("pausing " + rn.name)
            requests.put(rh.baseUrl + "/rendernodes/{name}/paused/".format(name=rn.name),
                         data=json.dumps({"paused": True, "killproc": False}))

    def onUnpauseAction(self):
        '''
        Slot called once the pause action is triggered
        '''
        rh = RequestHandler()
        for index in self.tableView.selectionModel().selectedRows():
            rn = index.data(Qt.UserRole)
            self.log.info("unpausing " + rn.name)
            requests.put(rh.baseUrl + "/rendernodes/{name}/paused/".format(name=rn.name),
                         data=json.dumps({"paused": False, "killproc": False}))

    def onXTermAction(self):
        '''
        Slot called once the XTerm action is triggered.
        '''
        for index in self.tableView.selectionModel().selectedRows():
            rn = index.data(Qt.UserRole)
            cu = currentUser().name
            self.log.debug("opening xterm for user {0}@{1}".format(cu, rn.host))
            try:
                subprocess.Popen(["xterm", "-e", "ssh", "{0}@{1}".format(cu, rn.host)])
            except:
                msg = "Could not open xterm."
                self.log.exception(msg)
                QMessageBox.critical(None, "Error", msg)

    def onVncAction(self):
        '''
        Slot called once the Show VNC action is triggered.
        '''
        config = Config()
        for index in self.tableView.selectionModel().selectedRows():
            rn = index.data(Qt.UserRole)
            vncCommand = config.vncCommand.format(hostname=rn.host)
            self.log.debug("opening vnc with command: {0}".format(vncCommand))
            try:
                subprocess.Popen(vncCommand, shell=True)
            except:
                msg = "Could not open VNC with command: {0}".format(vncCommand)
                self.log.exception(msg)
                QMessageBox.critical(None, "Error", msg)

    def __addAction(self, text, aId, selectionSensitive):
        a = Action(text, "Rendernode", aId, selectionSensitive, self)
        self.addAction(a)
        self.tableView.addAction(a)
        return a

    def setupActions(self):
        '''
        Setup all Actions this panel provides.
        '''
        a = self.__addAction("Pause", 1, True)
        a.triggered.connect(self.onPauseAction)
        a = self.__addAction("Unpause", 12, True)
        a.triggered.connect(self.onUnpauseAction)
        a = self.__addAction("Restart", 2, True)
#         a.triggered.connect(self.onPauseAction)
        a = self.__addAction("Kill and Pause", 3, True)
#         a.triggered.connect(self.onPauseAction)
        a = self.__addAction("Kill and Restart", 4, True)
#         a.triggered.connect(self.onPauseAction)
        a = self.__addAction("Quarantine", 5, True)
#         a.triggered.connect(self.onPauseAction)
        a = self.__addAction("Unquarantine", 6, True)
#         a.triggered.connect(self.onPauseAction)
        a = self.__addAction("Delete", 7, True)
#         a.triggered.connect(self.onPauseAction)
        a = self.__addAction("Show Log", 8, True)
#         a.triggered.connect(self.onPauseAction)
        a = self.__addAction("Open XTerm", 9, True)
        a.triggered.connect(self.onXTermAction)
        a = self.__addAction("Open VNC", 10, True)
        a.triggered.connect(self.onVncAction)
        a = self.__addAction("Remove Pools", 11, True)
#         a.triggered.connect(self.onPauseAction)
