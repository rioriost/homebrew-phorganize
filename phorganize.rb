class Phorganize < Formula
  include Language::Python::Virtualenv

  desc "Phorganize is a python script to organize photos and videos using embedded meta data in the files."
  homepage "https://github.com/rioriost/homebrew-phorganize/"
  url "https://files.pythonhosted.org/packages/47/24/f5578804ef253b18a1006c68e7c4ba9638ee7ee72cef2e035700cdb29add/phorganize-0.1.2.tar.gz"
  sha256 "3465bbb140e146ebc98a0bea004def2611f3abf84251a9465cc1388d7b624e76"
  license "MIT"

  depends_on "python@3.11"

  resource "python-magic" do
    url "https://files.pythonhosted.org/packages/da/db/0b3e28ac047452d079d375ec6798bf76a036a08182dbb39ed38116a49130/python-magic-0.4.27.tar.gz"
    sha256 "c1ba14b08e4a5f5c31a302b7721239695b2f0f058d125bd5ce1ee36b9d9d3c3b"
  end

  def install
    virtualenv_install_with_resources
  end

  test do
    system "#{bin}/phorganize", "--help"
  end
end
